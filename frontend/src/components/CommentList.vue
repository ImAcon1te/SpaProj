<!--
<template>
  <div class="comments-container">
    <button @click="showCommentForm">Комментировать</button>
    <CommentForm v-if="activeCommentForReply" :parent-id="activeCommentForReply.id" @comment-submitted="handleCommentSubmitted" />
    <h2>Комментарии</h2>
    <ul class="comments-list">
      <li v-for="comment in topLevelComments" :key="comment.id" class="comment">
        <CommentItem
          :comment="comment"
          :default-avatar="defaultAvatar"
          @reply-to-comment="replyToComment"
        />
      </li>
    </ul>
  </div>
</template>
-->
<template>
  <div class="comments-container">
    <button @click="showCommentForm">Комментировать</button>

    <CommentForm v-if="showForm" :parent-id="activeCommentForReply?.id" @comment-submitted="handleCommentSubmitted" />
    <h2>Комментарии</h2>
    <ul class="comments-list">
      <li v-for="comment in topLevelComments" :key="comment.id" class="comment">
        <CommentItem

          :comment="comment"
          :default-avatar="defaultAvatar"
          @reply-to-comment="replyToComment"
        />
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';
import CommentItem from './CommentItem.vue';
import CommentForm from './CommentForm.vue';

export default {
  components: {
    CommentForm,
    CommentItem
  },
  data() {
    return {
      comments: [],
      defaultAvatar: 'https://thumbs.dreamstime.com/b/%D0%B7%D0%BD%D0%B0%D1%87%D0%BE%D0%BA-%D0%BF%D0%BE-%D1%83%D0%BC%D0%BE%D0%BB%D1%87%D0%B0%D0%BD%D0%B8%D1%8E-%D0%BF%D0%BB%D0%BE%D1%81%D0%BA%D0%B8%D0%B9-%D0%B0%D0%B2%D0%B0%D1%82%D0%B0%D1%80-%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D1%8F-%D1%81%D0%BE%D1%86%D0%B8%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9-%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80-184330869.jpg',
      activeCommentForReply: null,
      showForm: false,
    };
  },
  computed: {
    topLevelComments() {
      return this.comments.filter(c => !c.parent);
    }
  },
  created() {
       axios.interceptors.request.use(config => {
          if (config.method === 'post') {
            config.headers['X-CSRFToken'] = this.getCSRFToken();
          }
          return config;
        }, error => {
          return Promise.reject(error);
        });
    this.fetchComments();
  },
  methods: {
      getCSRFToken() {
      let csrfToken = '';
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        let [name, value] = cookie.split('=');
        if (name.trim() === 'csrftoken') {
          csrfToken = value;
          break;
        }
      }
      return csrfToken;
    },
    fetchComments() {
      axios.get('http://localhost:8000/api/comments/')
        .then(response => {
          this.comments = this.buildCommentsTree(response.data);
        })
        .catch(error => {
          console.error('Ошибка получения комментария:', error);
        });
    },
    buildCommentsTree(comments) {
      let map = {}, node, roots = [], i;

      for (i = 0; i < comments.length; i += 1) {
        map[comments[i].id] = i;
        comments[i].replies = [];
      }

      for (i = 0; i < comments.length; i += 1) {
        node = comments[i];
        if (node.parent !== null) {
          comments[map[node.parent]].replies.push(node);
        } else {
          roots.push(node);
        }
      }
      return roots;
    },
    replyToComment(comment) {
      this.activeCommentForReply = comment;
      this.showForm = true;
    },
    showCommentForm() {
        this.showForm = true;
        this.activeCommentForReply = null;
      },
     handleCommentSubmitted() {
        this.showForm = false;
        this.activeCommentForReply = null;
        this.fetchComments();
      },
  }
};
</script>


<style>

.comments-container {
  margin: 20px;
  font-family: Arial, sans-serif;
}

.comments-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.comment {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
  padding-bottom: 15px;
  //border-bottom: 1px solid #e1e1e1;
}

.comment.reply {
  margin-left: 30px;
  border-left: 2px solid #e1e1e1;
  padding-left: 20px;
}

.comment-avatar {
  margin-right: 10px;
}

.comment-avatar img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.comment-body {
  flex-grow: 1;
}

.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.comment-author {
  font-weight: bold;
  margin-right: 10px;
  font-size: 14px;
}

.comment-date {
  font-size: 12px;
  color: #999;
}

.comment-content {
  font-size: 14px;
}

.replies {
  margin-top: 10px;
  margin-left: 20px;
  padding-left: 10px;
  border-left: 2px solid #e1e1e1;
}

</style>

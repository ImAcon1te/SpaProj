<template>
  <div :class="{ 'comment': true, 'reply': comment.parent }">
    <div class="comment-body">
      <div class="comment-header">
        <div class="comment-avatar">
          <img :src="comment.avatar || defaultAvatar" :alt="`${comment.username}'s avatar`" />
        </div>
        <h5 class="comment-author">{{ comment.username }}</h5>
        <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
        <button class="reply-button" @click="emitReplyToComment">Ответить</button>
      </div>
      <div class="comment-content" v-html="comment.text"></div>
      <div class="comment-file" v-if="comment.image">
            <i>Добавленые файлы</i><br>
      </div>
      <ul class="comments-list">
        <li v-for="reply in comment.replies" :key="reply.id" class="comment">
          <CommentItem

            :comment="reply"
            :default-avatar="defaultAvatar"
            @reply-to-comment="$emit('reply-to-comment', $event)"
          />
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  props: {
    comment: Object,
    defaultAvatar: String
  },
    created() {
    if(this.comment.image !== null){
        this.loadFile();
    }
  },
  methods: {
  loadFile() {
     try {
        axios.get(this.comment.image, { responseType: 'blob' })
          .then((response) => {
            const reader = new FileReader();
            reader.onload = () => {
              const fileContent = reader.result;
              const dataType = fileContent.split(';')[0];
              if (dataType == 'data:text/plain') {
                const fileName = this.comment.image.split('/')[4];
                console.log(this.comment.image.split('/'))
                const fileNameSpan = document.createElement('span');
                fileNameSpan.textContent = fileName;
                fileNameSpan.classList.add('file-name');
                const fileContentP = document.createElement('p');
                fileContentP.textContent = decodeURIComponent(escape(atob(fileContent.split(',')[1])));
                this.$el.querySelector('.comment-file').appendChild(fileNameSpan);
                this.$el.querySelector('.comment-file').appendChild(fileContentP);
              } else {
                const img = document.createElement('img');
                img.src = fileContent;
                img.style.maxWidth = '320px';
                img.style.maxHeight = '240px';
                this.$el.querySelector('.comment-file').appendChild(img);
              }
            };
            reader.readAsDataURL(response.data);
          });
      } catch (error) {
        console.error('Error loading file:', error);
      }
    },
    emitReplyToComment() {
      this.$emit('reply-to-comment', this.comment);
    },
    formatDate(dateString) {
      const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
      return new Date(dateString).toLocaleDateString('ru-RU', options).replace(/(\d{2})\.(\d{2})\.(\d{4}), (\d{2}):(\d{2}):(\d{2})/, '$1-$2-$3 $4:$5:$6');
    }
  }
};
</script>
<style scoped>

.comment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #f5f5f5; /* Цвет фона шапки комментария */
  padding: 10px;
  border-radius: 4px;
}

.reply-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 15px;
}

.reply-button:hover {
  background-color: #0056b3;
}
img {
  max-width: 320px;
  max-height: 240px;
}
.comment-file{
    margin-top: 15px;
    border-bottom: 2px solid grey;
    border-top: 2px solid grey;
}
.comment-file img{
  max-width: 320px;
  max-height: 240px;
}
</style>
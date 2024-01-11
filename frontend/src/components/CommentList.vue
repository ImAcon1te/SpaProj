<template>
    <div>
        <!-- Если пользователь не авторизован, показываем кнопки "регистрация" и "авторизация" -->
        <div v-if="!isAuthenticated">
          <button @click="showRegistrationForm">Регистрация</button>
          <button @click="showLoginForm">Авторизация</button>
        </div>

        <!-- Если пользователь авторизован, показываем аватар, имя и кнопку "редактировать профиль" -->
        <ProfileItem :user=user
                    :defaultAvatar=defaultAvatar
                    @update-user="handleUpdateUser"
                    v-if="isAuthenticated"  />

        <!-- Если пользователь выбрал "регистрацию", показываем форму регистрации -->
        <RegisterForm v-if="showRegistration"  @register-submitted="handleRegisterSubmitted" @close-form="closeRegistrationForm"/>

        <!-- Если пользователь выбрал "авторизацию", показываем форму авторизации -->
        <div v-else-if="showLogin">
          <form @submit.prevent="login">
            <input v-model="username" type="text" placeholder="Username" />
            <input v-model="password" type="password" placeholder="Password" />
            <button type="submit">Login</button>
          </form>
        </div>
  </div>

  <!-- Контейнер комментариев -->
  <div class="comments-container">
    <button @click="showCommentForm" @close-form="closeCommentForm">Комментировать</button>

    <!-- Если пользователь выбрал "комментировать", показываем форму добавления комментария -->
    <CommentForm :user=user v-if="showForm" :parent-id="activeCommentForReply?.id" @comment-submitted="handleCommentSubmitted" @close-form="closeCommentForm"/>
    <h2>Комментарии</h2>
    <ul class="comments-list">
      <li v-for="comment in topLevelComments" :key="comment.id" class="comment">
        <CommentItem
          :comment="comment"
          :default-avatar="defaultAvatar"
          @reply-to-comment="replyToComment"
          @update-avatar="handleUpdateAvatar"
        />
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';
import CommentItem from './CommentItem.vue';
import CommentForm from './CommentForm.vue';
import RegisterForm from './RegisterForm.vue';
import ProfileItem from './ProfileItem.vue';
export default {
  components: {
    CommentForm,
    CommentItem,
    RegisterForm,
    ProfileItem,
  },
  data() {
    return {
      comments: [],
      defaultAvatar: 'https://thumbs.dreamstime.com/b/%D0%B7%D0%BD%D0%B0%D1%87%D0%BE%D0%BA-%D0%BF%D0%BE-%D1%83%D0%BC%D0%BE%D0%BB%D1%87%D0%B0%D0%BD%D0%B8%D1%8E-%D0%BF%D0%BB%D0%BE%D1%81%D0%BA%D0%B8%D0%B9-%D0%B0%D0%B2%D0%B0%D1%82%D0%B0%D1%80-%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D1%8F-%D1%81%D0%BE%D1%86%D0%B8%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9-%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80-184330869.jpg',
      activeCommentForReply: null,
      showForm: false,
      // для авторизации
      user: {
        id: '',
        username: '',
        email: '',
        image: null,
        avatar: null,
      },
      isAuthenticated: false,
      showRegistration: false,
      showLogin: false,
    };
  },
  mounted() {
    // Проверяем авторизацию при загрузке компонента
    this.checkAuthentication();
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
    handleUpdateUser(updatedUser) {
      // Обновляем пользователя в данных
      this.user = updatedUser;
    },
    handleUpdateAvatar(userProfileId, avatarUrl) {
      const matchingComments = this.comments.filter(comment => comment.user_profile === userProfileId);
      matchingComments.forEach(comment => {
         comment.avatar = avatarUrl;
       });
    },
     checkAuthentication() {
      // Делаем запрос к API для получения информации о пользователе
      // В противном случае, оставляем его false
      axios.get('http://localhost:8000/api/user-info/')
      .then(response  => {
          if (response.data.authenticated) {
              this.isAuthenticated = true;
              //console.log(response.data.username)
            } else {
              this.isAuthenticated = false;
            }
        })
        .catch(() => {
          this.isAuthenticated = false;
        });
    },
    showRegistrationForm() {
      this.showRegistration = true;
      this.showLogin = false;
    },
    showLoginForm() {
      this.showLogin = true;
      this.showRegistration = false;
    },
    login() {
      const accountData = new FormData();
      accountData.append('username', this.username);
      accountData.append('password', this.password);
      axios.post('http://localhost:8000/api/login/', accountData, { withCredentials: true, headers: { 'Content-Type': 'multipart/form-data' } })
      .then(accountResponse => {
         //console.log('Успешно авторизован!', accountResponse.data);
         this.isAuthenticated = true;
         this.user.id = accountResponse.data.id;
         this.user.username = accountResponse.data.username;
         this.user.email = accountResponse.data.email;
         this.user.avatar = accountResponse.data.image;
         this.showLogin = false;
      })
      .catch(accountError => {
         this.isAuthenticated = false;
         alert('Неправильная пара логин/пароль')
         console.error('Неправильная пара логин/пароль:', accountError);
      });
    },
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
          //console.log(this.comments);
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
      handleRegisterSubmitted(userData) {
        this.user.id = userData.id;
        this.user.username = userData.username;
        this.user.email = userData.email;
        //console.log('авторизован!')
        //console.log(this.user)
        this.isAuthenticated = true;
        this.showRegistration = false;
        this.showLogin = false;
      },
       closeRegistrationForm() {
        this.showRegistration = false;
      },
      closeCommentForm(){
        this.showForm = false;
        this.activeCommentForReply = null;
      }
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

.comment-avatar img{
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

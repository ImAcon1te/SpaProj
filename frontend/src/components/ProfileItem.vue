<template>
  <div>
    <div v-if="!editing" class=comment-profile>
      <!-- <img :src="user.avatar || defaultAvatar" alt="Avatar" /> -->
      <h2>Аккаунт: {{ user.username }}</h2>
      <p>{{ user.email }}</p>
      <button @click="editProfile">Загрузить другую аватарку</button>
    </div>

    <div v-else>
      <form @submit.prevent="saveProfile">
        <label for="newAvatar">Загрузить новый Avatar:</label>
        <input type="file" ref="imageInput"  @change="handleFileUpload" id="newAvatar" accept="image/*" />
        <br>
        <button type="submit">Сохранить</button>
      </form>
      <button @click="cancelEdit">Отмена</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    defaultAvatar: String,
    user: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      editing: false,
      editedUser: {
        username: this.user.username,
        email: this.user.email,
        avatar: this.user.avatar,
      },
      newAvatarFile: null,
    };
  },
  mounted() {
       axios.interceptors.request.use(config => {
          if (config.method === 'post') {
            config.headers['X-CSRFToken'] = this.getCSRFToken();
          }
          return config;
        }, error => {
          return Promise.reject(error);
        });
  },
  methods: {
  loadAvatarImage() {
    axios.get(`http://localhost:8000/profile/${this.user.id}`, { responseType: 'blob' })
      .then((response) => {
        const reader = new FileReader();
        reader.onload = () => {
          // Испускаем событие обновления пользователя с новым аватаром
          this.$emit('update-user', { ...this.user, avatar: reader.result });
        };
        reader.readAsDataURL(response.data);
      })
      .catch((error) => {
        console.error('Ошибка при загрузке изображения для аватара:', error);
      });
  },
    getCSRFToken() {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        let [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
          return value;
        }
      }
      return null;
    },
    saveProfile() {
  try {
    const csrfToken = this.getCSRFToken();
    const userData = new FormData();
    userData.append('avatar', this.newAvatarFile);
    const response = axios.put('http://localhost:8000/api/profile/', userData, {
      withCredentials: true,
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-CSRFToken': csrfToken,
      },
    });

    // Проверяем наличие свойства avatar в ответе
        const updatedUser = {
          ...this.user,
          avatar: response.data ? response.data.avatar : null,
        };
        // Испускаем событие обновления пользователя в родительский компонент
        this.$emit('update-user', updatedUser);
    this.editing = false;
  } catch (error) {
    console.error('Ошибка при сохранении нового изображения:', error);
  }
},

    editProfile() {
      this.editing = true;
    },
    cancelEdit() {
      this.editing = false;
    },
    handleFileUpload() {
      const fileInput = this.$refs.imageInput;
      if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const img = new Image();

        img.onload = () => {

          this.newAvatarFile = file;
        };
        img.src = URL.createObjectURL(file);
      }
    },
  },
};
</script>


<style scoped>

.comment-profile img{
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

</style>

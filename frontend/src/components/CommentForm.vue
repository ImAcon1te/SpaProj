<template>
<div class="overlay">
 <div class="form-container">
  <form @submit.prevent="submitComment">
    <div>
      <label for="username">User Name:</label>
      <input type="text" id="username" v-model.trim="comment.username" required />
    </div>

    <div>
      <label for="email">E-mail:</label>
      <input type="email" id="email" v-model.trim="comment.email" required />
    </div>

    <div>
      <label for="homepage">Home Page:</label>
      <input type="url" id="homepage" v-model.trim="comment.homepage" />
    </div>

    <div>
      <div v-if="isHtmlInvalid" class="error">
        Введенный текст содержит запрещенные или незакрытые HTML теги!
      </div>
      <label for="text">Text:</label>
      <textarea id="text" v-model="comment.text" required></textarea>
    </div>

    <div>
          <label for="image">Upload Image:</label>
          <input type="file" id="image" ref="imageInput" accept="image/jpeg, image/png, image/gif, text/plain" @change="handleFileChange" />
    </div>

    <div>
        <label for="captcha">CAPTCHA:</label>
        <img :src="captchaImageUrl" alt="CAPTCHA" v-if="captchaImageUrl"/>
        <input type="text" id="captcha" v-model="captchaResponse" required />
     </div>
    <button type="submit">Submit</button>
  </form>
  </div>
 </div>
</template>

<script>
import axios from 'axios';
import DOMPurify from 'dompurify';
export default {
  props: {
    parentId: {
      type: Number,
      default: null
    }
  },
  components: {

  },
  data() {
    return {
      captchaImageUrl: '',
      captchaResponse: '',
      comment: {
        username: '',
        email: '',
        homepage: '',
        text: '',
        image: null,
      },

    };
  },
  mounted() {
    this.fetchCaptcha();
  },
  methods: {
  processImageFile(file){
  const img = new Image();
  img.onload = () => {
    this.comment.image = file;
  };
  img.src = URL.createObjectURL(file);
},
  processTextFile(file){
  if (file.size > 100 * 1024) {
    alert('Файл должен быть менее 100 KB');
      file.value = '';
      this.comment.image = null;
      return;
    } else {
      const reader = new FileReader();
    reader.onload = () => {
      const fileContent = reader.result;
      this.comment.image = fileContent;
    };
    // Читаем содержимое файла как текст
    reader.readAsText(file);
  }
},
  handleFileChange() {
  const fileInput = this.$refs.imageInput;
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    if (!file.type.startsWith('image/') && file.type !== 'text/plain') {
      alert('Неподходящий тип файла. Пожалуйста, отправьте изображение (JPG, GIF, PNG) или текстовый файл (TXT).');
      fileInput.value = '';
      this.comment.image = null;
      return;
    } else if (file.type == 'text/plain') {
      if (file.size > 100 * 1024) {
        alert('Файл должен быть менее 100 KB');
        fileInput.value = '';
        this.comment.image = null;
        return;
      } else {
        console.log('файл текстовый формат ок')
        const reader = new FileReader();
        reader.onloadstart = () => {
          console.log('Начало чтения файла');
        };
        reader.onprogress = (event) => {
          console.log('Прогресс чтения файла:', event.loaded, event.total);
        };
        reader.onload = () => {
          console.log('Чтение файла завершено');
          //const fileContent = reader.result;
          console.log('Содержимое файла:', reader.result);
          this.comment.image = file;
        };
        reader.onerror = (error) => {
          console.error('Ошибка чтения файла:', error);
        };
        // Читаем содержимое файла как текст
        reader.readAsText(file);
      }
    } else if (file.type.startsWith('image/')) {
      const img = new Image();
      img.onloadstart = () => {
        console.log('Начало загрузки изображения');
      };
      img.onload = () => {
        console.log('Загрузка изображения завершена');
        this.comment.image = file;
      };
      img.src = URL.createObjectURL(file);
    }
  }
},


  fetchCaptcha() {
      axios.get('http://localhost:8000/api/generate-captcha/')
      .then(response => {
         this.captchaImageUrl = 'http://localhost:8000' + response.data.image_url;
         this.captchaKey = response.data.key;
      })
      .catch(error => {
        console.error('Ошибка при загрузке капчи:', error);
      });
    },
    submitComment() {
    const commentData = new FormData();
    commentData.append('username', this.comment.username);
    commentData.append('email', this.comment.email);
    commentData.append('homepage', this.comment.homepage);
    commentData.append('text', this.comment.text);
    if (this.comment.image !== null){
        commentData.append('image', this.comment.image);
    }
    if (this.parentId !== null){
        commentData.append('parent', this.parentId);
    }
axios.post('http://localhost:8000/api/сheck-captcha/', { captcha_text: this.captchaResponse, captcha_key: this.captchaKey }, { withCredentials: true })
  .then(response => {
    if (response.data.success) {
      axios.post('http://localhost:8000/api/comments/', commentData, { withCredentials: true, headers: { 'Content-Type': 'multipart/form-data' } })
        .then(commentResponse => {
          console.log('Комментарий добавлен!', commentResponse.data);
          this.$emit('comment-submitted');
          this.resetForm();
        })
        .catch(commentError => {
          console.error('Ошибка при сохранении комментария:', commentError);
        });
    } else {
      console.error('Неправильная CAPTCHA');
    }
  })
  .catch(error => {
    console.error('Ошибка при проверке CAPTCHA:', error);
  });
},
    resetForm() {
      this.comment = { username: '', email: '', homepage: '', text: '' , image: null};
    },
    cleanText() {
      this.comment.text = this.comment.text.replace(/<(?!\/?(a|code|i|strong)(?=>|\s.*>))\/?.*?>/g, '');
    }
  },
  computed: {
        topLevelComments() {
      return this.comments.filter(c => !c.parent);
    },
      isHtmlInvalid() {
        if (!this.comment.text || typeof this.comment.text !== 'string') {
          return false;
        }

        const cleanedHtml = DOMPurify.sanitize(this.comment.text, {
          ALLOWED_TAGS: ['a', 'code', 'i', 'strong'],
        });
        return cleanedHtml !== this.comment.text;
          },
    },
};
</script>

<style scoped>
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.form-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  width: 100%;
  max-width: 400px;
  margin: auto;
}

form {
  background: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  width: 100%;
}

form div {
  margin-bottom: 10px;
  text-align: center;
}

label {
  display: block;
  margin-bottom: 5px;
  width: 100%;
}


input[type="text"],
input[type="email"],
input[type="url"],
textarea {
  width: calc(100% - 20px);
  margin: 10px 0;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}


button[type="submit"] {
  width: calc(100% - 20px);
  padding: 10px;
  margin-top: 10px;
  border-radius: 4px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
}
textarea {
  resize: none;
}

button[type="submit"]:hover {
  background-color: #0056b3;
}
</style>

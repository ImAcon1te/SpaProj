<template>
<div class="overlay">
 <div class="form-container">
  <div class="close-button">
    <button @click="closeForm">×</button>
  </div>
  <form @submit.prevent="register">

    <div>
      <label for="email">Email:</label>
      <input v-model="email" type="email" required />
    </div>

    <div>
      <label for="login">Login:</label>
      <input v-model="login" type="text" required />
    </div>

    <div>
      <label for="password">Password:</label>
      <input v-model="password" type="password" required />
    </div>

    <div>
      <label for="reply_password">Repeat Password:</label>
      <input v-model="replyPassword" type="password" required />
    </div>
    <div>
        <label for="captcha">CAPTCHA:</label>
        <img :src="captchaImageUrl" alt="CAPTCHA" v-if="captchaImageUrl"/>
        <input type="text" id="captcha" v-model="captchaResponse" required />
     </div>
    <button type="submit">Register</button>
  </form>
  </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      captchaImageUrl: '',
      captchaResponse: '',
      email: '',
      login: '',
      password: '',
      replyPassword: '',
    };
  },
  mounted() {
    this.fetchCaptcha();
  },
  methods: {
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
    register() {
      // Проверка пароля и его подтверждения
        if (this.password !== this.replyPassword) {
            alert("Passwords do not match.");
            return;
        }
        // Логика отправки данных на сервер для регистрации
        const accountData = new FormData();
        accountData.append('email', this.email);
        accountData.append('username', this.login);
        accountData.append('password', this.password);
        axios.post('http://localhost:8000/api/сheck-captcha/', { captcha_text: this.captchaResponse, captcha_key: this.captchaKey }, { withCredentials: true })
          .then(response => {
            if (response.data.success) {
              axios.post('http://localhost:8000/api/register/', accountData, { withCredentials: true, headers: { 'Content-Type': 'multipart/form-data' } })
                .then(accountResponse => {
                  console.log('Аккаунт создан!', accountResponse.data);
                  this.$emit('register-submitted', accountResponse.data);
                })
                .catch(accountError => {
                  alert('Ошибка при создании аккаунта')
                  console.error('Ошибка при оздании аккаунта:', accountError);
                });
            } else {
              alert('Неправильная CAPTCHA')
              console.error('Неправильная CAPTCHA');
            }
          })
          .catch(error => {
            console.error('Ошибка при проверке CAPTCHA:', error);
          });
    },
     closeForm(){
       this.$emit('close-form');
     },
  },
};
</script>

<style scoped>
.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 20px;
  width: 30px;
  height: 30px;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  background: none;
  border: none;
  outline: none;
}

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
input[type="password"],
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
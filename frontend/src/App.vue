<template>
  <div>
    <!--
    <router-link to="/">Главная</router-link>
    <router-link to="/add-comment">Добавить комментарий</router-link>
      -->

    <router-view></router-view>
  </div>
</template>

<script>
import router from './router';

export default {
  name: 'App',
  router,
};
</script>

<style>

</style>



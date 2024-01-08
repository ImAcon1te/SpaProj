/*
import Vue from 'vue';
import VueRouter from 'vue-router';

Vue.use(VueRouter);

// Импортируйте ваши компоненты
//import CommentList from './components/CommentList.vue';
import CommentForm from './components/CommentForm.vue';
import HelloWorld from './components/HelloWorld.vue';
const routes = [
  //{ path: '/', component: CommentList, props: { comments: [] } }, // Передайте пустой массив, который будет заполнен данными с сервера
  { path: '/', component: HelloWorld },
  { path: '/add-comment', component: CommentForm },
  // Другие маршруты
];

const router = new VueRouter({
  routes,
  mode: 'history',
});

export default router;
*/
import { createRouter, createWebHistory } from 'vue-router';
import CommentForm from './components/CommentForm.vue';
import HelloWorld from './components/HelloWorld.vue';
import CommentList from './components/CommentList.vue';
const routes = [
  { path: '/', component: CommentList, props: { comments: [] } },
  { path: '/test', component: HelloWorld},
  { path: '/add-comment', component: CommentForm },
  // Другие маршруты
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

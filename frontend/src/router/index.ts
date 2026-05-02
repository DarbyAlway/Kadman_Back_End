// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import Layout from '../views/Layout.vue';
import Attendance from '../views/Attendance.vue';
import Payments from '../views/Payments.vue';

const routes = [
  {
    path: '/',
    redirect: '/layout'
  },
  {
    path: '/layout',
    name: 'Layout',
    component: Layout
  },
  {
    path: '/attendance',
    name: 'Attendance',
    component: Attendance
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
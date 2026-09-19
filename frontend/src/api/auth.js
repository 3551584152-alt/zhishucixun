import { get, post } from './request'
export function login(username, password) { return post('/api/auth/login', { username, password }) }
export function register(username, password, nickname) { return post('/api/auth/register', { username, password, nickname }) }
export function fetchMe() { return get('/api/auth/me') }
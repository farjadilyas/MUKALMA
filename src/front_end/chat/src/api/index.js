import axios from 'axios'

const API = axios.create({ baseURL: "http://4c94-35-238-238-160.ngrok.io" });

export const sendMessage = (message) => API.post('/reply', message)
export const fetchSource = () => API.get('/source')
export const fetchTopics = () => API.get('/topics')
export const changeTopic = (topic) => API.post('/topics/select', topic)

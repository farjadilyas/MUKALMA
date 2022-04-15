import axios from 'axios'

const API = axios.create({ baseURL: "http://569a-206-84-140-3.ngrok.io" });

export const sendMessage = (message) => API.post('/reply', message)
export const waitForResponse = () => API.get('/get_update')

export const fetchSource = () => API.get('/source')
export const fetchTopics = () => API.get('/topics')

export const changeTopic = (topic) => API.post('/topics/select', topic)

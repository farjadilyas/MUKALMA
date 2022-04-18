import axios from 'axios'

const API = axios.create({ baseURL: "https://97f2-206-84-140-3.ngrok.io" });

export const sendMessage = (message) => API.post('/reply', message)
export const waitForResponse = () => API.get('/get_update')
export const clearContext = () => API.get('/clear_context')

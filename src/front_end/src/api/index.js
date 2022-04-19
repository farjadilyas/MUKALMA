import axios from 'axios'

const API = axios.create({ baseURL: "http://3fb7-35-238-228-239.ngrok.io" });

export const sendMessage = (message) => API.post('/reply', message)
export const waitForResponse = () => API.get('/get_update')
export const clearContext = () => API.get('/clear_context')

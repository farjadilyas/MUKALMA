import axios from 'axios'

export var API = axios.create({ baseURL: "http://127.0.0.1:5000" });
export const updateApiUrl = (url) => {
    API = axios.create({ baseURL: url });
}

export const sendMessage = (message) => API.post('/reply', message);
export const waitForResponse = () => API.get('/get_update');
export const clearContext = () => API.get('/clear_context');
export const connect = () => API.get('/connect');
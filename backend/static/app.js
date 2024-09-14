new Vue({
    el: '#app',
    data: {
        message: 'Hello from Vue.js!',
        apiMessage: ''
    },
    created() {
        axios.get('/api/data')
            .then(response => {
                this.apiMessage = response.data.message;
            })
            .catch(error => {
                console.error('There was an error!', error);
            });
    },
    template: '<div>{{ message }}<br>{{ apiMessage }}</div>'
});
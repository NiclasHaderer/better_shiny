export const rerenderHandler = (data) => {
    const html = data.html;
    const id = data.id;

    const element = document.getElementById(id);
    element.innerHTML = html;
}


export const errorResponseHandler = (data) => {
    console.error(data.error)
}
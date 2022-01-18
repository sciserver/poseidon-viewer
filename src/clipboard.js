import Vue from 'vue';

export function copyTextToClipboard(text) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        document.execCommand('copy');
        Vue.notify({
            group: 'notify',
            type: 'success',
            duration: 1000,
            position: 'bottom center',
            text: 'Data copied to clipboard'
        });
    } catch (error) {
        Vue.notify({
            group: 'notify',
            type: 'error',
            duration: 1000,
            position: 'bottom center',
            text: error
        });
    }

    document.body.removeChild(textArea);
}

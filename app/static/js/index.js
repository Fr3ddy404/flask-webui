function toggleFields() {
    const prompt_name_Field = document.getElementById('prompt_name');
    const promptField = document.getElementById('prompt');
    if (prompt_name_Field.disabled) {
        prompt_name_Field.disabled = false;
        promptField.disabled = false;        
    } else {
        prompt_name_Field.disabled = true;
        promptField.disabled = true;
    }
}

function handleSelectionChange() {
    const selectedPromtId = document.getElementById('select_prompt').value;

    const name = document.getElementById('prompt_name');
    const content = document.getElementById('prompt');

    fetch(`/get_prompt/${selectedPromtId}`).then(response => response.json())
    .then(data => {
        name.value = data.name;
        content.value = data.content;
    });
    
}

function submitForm(action) {
    const form = document.getElementById('form');
    form.action = action;
    form.submit();
}


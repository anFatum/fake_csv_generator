let addButton = $("#add_more")
addButton.on('click', addForm)

$("input[name^='del_btn']").each(function () {
    $(this).on("click", removeFromModels)
})

$("select[name$=field_type]").each(function () {
    $(this).on("change", handleFieldType)
})

function addForm(e) {
    e.preventDefault()
    cloneMore("#empty_form", 'fields')
    cleanForm("#empty_form")
}

function cloneMore(selector, type) {
    const type_field = $(selector).find('option:selected').val();
    let newElement = $(selector).clone(true);
    let total = $('#id_' + type + '-TOTAL_FORMS').val();
    newElement.find(':input').each(function () {
        let name = $(this).attr('name').replace('__prefix__', total);
        let id = 'id_' + name;
        const isSelect = $(this).find("option:selected").val();
        $(this).attr({'name': name, 'id': id}).removeAttr('checked');
        if (isSelect)
            $(this).val(type_field)
        if ($(this).attr("name").includes("order"))
            $(this).val($(this).val() || total)
    });
    newElement.find('label').each(function () {
        let newFor = $(this).attr('for').replace('__prefix__', total);
        $(this).attr('for', newFor);
    });
    total++;
    newElement.removeAttr("id")
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $('#form_set').append(newElement);
}

function cleanForm(selector) {
    $(selector).find(':input').each(function () {
        if ($(this).attr("type") !== "submit")
            $(this).val("")
    });
}

function removeFromModels(e) {
    e.preventDefault();
    deleteForm("fields", e.target);
}

function deleteForm(prefix_tag, btn) {
    const idString = '#id_' + prefix_tag + '-TOTAL_FORMS';
    if (!btn.closest('table').getAttribute("id"))
        btn.closest('table').remove();
    const forms = $('table');
    const formLength = forms.length - 1;
    $(idString).val(formLength);
    for (let i = 0, formCount = formLength; i < formCount; i++) {
        $(forms.get(i)).find(':input').each(function () {
            updateElementIndex(this, prefix_tag, i);
        });
        $(forms.get(i)).find('label').each(function () {
            updateElementIndex(this, prefix_tag, i);
        });
    }
    return false;
}

function updateElementIndex(el, prefix_tag, ndx) {
    const id_regex = new RegExp('(' + prefix_tag + '-\\d+)');
    const replacement = prefix_tag + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

function handleFieldType(e) {
    const selectedOption = $(e.target).find("option:selected");
    const prefix = $(e.target).attr("name").split('-')[1];
    console.log(prefix);
    if (selectedOption.text() === "Integer") {
        changeNumberFieldVisibility(prefix, false)
    } else {
        changeNumberFieldVisibility(prefix, true)
    }
}

function changeNumberFieldVisibility(prefix, invisibilityState) {
    $(`#id_fields-${prefix}-from`).attr("hidden", invisibilityState)
    $(`label[for=id_fields-${prefix}-from]`).attr("hidden", invisibilityState)
    $(`#id_fields-${prefix}-to`).attr("hidden", invisibilityState)
    $(`label[for=id_fields-${prefix}-to]`).attr("hidden", invisibilityState)
}

{# Template built by support.py; Comments in these braces will not be rendered to the browser #}

var DUGattachment_total_size = {{script.attachment_total_size}}
var DUGattachment_max_size = {{script.attachment_max_size}}

var DUGvis = [
    {% for v in script.vis_classes %}
        '{{v}}',
    {% endfor %}
];

var DUGvalueClasses = {
    {% for k,v in script.vis_values.items() %}
        '{{k}}': '{{v}}',
    {% endfor %}
};

var DUGexpectedTypes = {
    {% for k,v in script.expected_types.items() %}
        '{{k}}': '{{v}}',
    {% endfor %}
}

function setVisible(typeKey) {
    if (typeKey == undefined)
        return;

    for(vis_class of DUGvis) {
        $('.'.concat(vis_class)).toggle(typeKey == vis_class);
    }
}

function valueClass(typeKey) {
    for (var k in DUGvalueClasses) {
        if (typeKey == k)
           return DUGvalueClasses[k];
    }
    return undefined;
}

function onVisSelection() {
    $("#{{script.type_id}} option:selected").each(function() {
        var selectedType = $(this).val();
        var vc = valueClass(selectedType);
        $('.vis').each(function() {
            var vis = $(this).hasClass(vc) || $(this).hasClass('vis_all');
            $(this).toggle(vis);
            $(this).find('.required').toggleClass('enabled', vis);
        })
        $('#module option').each(function(idx, moduleVal) {
            $(moduleVal).toggle(moduleIsSensible(moduleVal.value, selectedType));
        })
        sanityCheck();
    });
}

function toggleWarningState(field) {
    field.toggleClass('warning', field.val().length == 0);
    field.parents('tr').find('td.compulsory').toggleClass('warning', field.val().length == 0);
    //Enable the warning message if any field is both flagged as a warning, and the field is enabled.
    sanityCheck();
}

function moduleIsSensible(moduleValue, type) {
    var expected = DUGexpectedTypes[moduleValue]
    return expected == "any" || type == expected
}

function prePopulate() {
    var date = $("#date")
    if (!date.val()) {
        var today = new Date()
        date.val(today.getDate() + "/" + (today.getMonth() + 1) + "/" + today.getFullYear())
    }
}

function sanityCheck() {
    function setWarningMessage(message, isFatal) {
        if (isFatal) {
            $('#submit').attr('disabled', "true")
        } else {
            $('#submit').removeAttr('disabled')
        }
        $('#warning_msg').toggleClass("warn", !isFatal)
        $('#warning_msg').toggle(true)
        $('#warning_msg').html(message)
    }

    function error(condition, message) {
        if (!condition)
            return false
        setWarningMessage(message, true)
        return true
    }
    
    function warn(condition, message) {
        if (!condition)
            return false
        setWarningMessage(message, false)
        return true
    }
    
    if (error(!$('#email').val(), '<p>Your username helps us contact you if we have a solution or need more information</p>')
        || error(!$('#subject').val(), '<p>A short descriptive title helps the right person get your message</p>')
        || error(!$('#type').val(), '<p>You must select a Type for your ticket for me to know where to send it.</p>')
        || error($('.filesize').length > 0, '<p>For large files, you may instead want to supply a directory.</p>')
        || error($('.redirect.enabled').length > 0, '<p>This support option requires you to use a different form. Please follow and bookmark the provided link.</p>')
        || error(sumSizes($('.filetotal')) > DUGattachment_total_size, '<p>The attachments exceed the maximum message size.<br/>Please instead provide a directory to the files in your description.<p>'))
        return


    if (warn($('.warning.enabled').length > 0, '<p>One or more important fields have not been supplied. This may prevent your ticket being handled in a timely manner.<p>'))
        return
    $('#warning_msg').toggle(false)
    $('#submit').removeAttr('disabled')
}

function sumSizes(fields) {
    sizes = 0
    fields.each(function(v) { sizes += parseInt($(this).text()); }) 
    return sizes
}

function validateEmail(field) {
    var val = field.val()
    if (val.length == 0)
        return;

    // currently all dug usernames consist only of a-z
    field.parent('td').find('.invalid').toggleClass('hidden', RegExp('^[a-zA-Z]*$').test(val) && val != "username")
}

function validateCC(field) {
    var val = field.val()
    if (val.length == 0)
        return;
    field.parent('td').find('.match_user').each(function() {
        var user = $(this).attr('contains');
        $(this).toggleClass('hidden', !val.includes(user));
    })
}

function validatePath(field) {
    var val = field.val()
    field.parent('td').find('.invalid').toggleClass('hidden', val.length == 0 || val.includes('/'))
}

function addValidation(selector, validationFn) {
    $(selector).each(function() {
        $(this).on('change keyup paste', function() {
            validationFn($(this));
        })
        validationFn($(this));
    });
}

function setConditional(destRow, srcField, matchValue) {
    var match = srcField.val() === matchValue;
    destRow.find('.label').toggleClass('compulsory warning', match);
    destRow.find('input, select').toggleClass('required warning', match);
}

function addConditional(selector, configFn) {
    $(selector).each(function() {
        var row = $(this);
        var name = row.attr('compulsory_key');
        var value = row.attr('compulsory_value');
        var src = $('#' + name);
        src.on('change keyup paste', function() {
            configFn(row, $(this), value);
        });
        configFn(row, src, value);
    })
}

function formatBytes(bytes) {
    if (bytes < 1024)
        return bytes + " Bytes"
    bytes /= 1024;
    if (bytes < 1024)
        return bytes.toFixed(2) + "KB"
    bytes /= 1024;
    return bytes.toFixed(2) + "MB"
}

//We're using a form, via cgi, so there's no running server back-end to suck up our uploads as we go.
//Browser security disallows access to the upload path. Instead, each upload is done using its own input element.
//Further, because validation is tied to the default input element, we need to reuse its id, and give the populated inputs new ids each time.
//If the user removes a selected upload, we simply delete its input element, hidden in its row.
function createNewAttachmentRow() {
    var parent = $('#atlist')
    var attachment_list = '<div class="attachmentList hidden"></div>'
    var static_path = 'static/'; //http://secure.dugeo.com/support-icon/static/'
    var remove_icon = '<img class="hidden atdel" src="' + static_path + 'delete.png" alt="Delete" title="Remove this attachment"></img><img class="atadd" src="' + static_path + 'attach.png" alt="Add another attachment"></img>'
    var input_line = '<div class="atfield"></div>'
    var row = parseInt(parent.attr('next'))
    parent.attr('next', row+1)

    var row_id = 'atr' + row
    var row_sel = '#' + row_id

    //Create a new row on the bottom and give it a unique id
    var markup = '<tr id="' + row_id + '"><td>' + remove_icon + '</td><td>' + attachment_list + input_line + '</td></tr>'
    $('#atlist').append(markup)

    //Clone the active attachments field where it is. Change the ID on the original and hide it. 
    var file_input = $('#attachments')
    var file_clone = file_input.clone()
    var new_id = 'attachments' + row
    file_input.attr('id', new_id)
    file_input.attr('name', new_id)
    file_input.addClass('hidden')    

    //Insert the clone into the new row, and make sure it looks new and shiny.
    file_clone.val('')
    file_clone.removeClass('hidden')
    $(row_sel + " .atfield").append(file_clone)

    //If we click on the delete button, drop the whole row, including the associated input field
    $(row_sel + ' .atdel').click(function(event) {
        event.preventDefault()
        $(row_sel).remove()
        sanityCheck()
    })

    //On any new upload being selected, show the summary & delete button, hide the input field, and create a new row
    $(row_sel + ' input').on('change keyup paste', function() {            
        $(this).addClass('hidden')
        var summary = $(row_sel + ' .attachmentList')
        summary.removeClass('hidden')
        var files = $(this).prop('files')
        var names = [];
        var isError = false
        var total = 0
        for(var i = 0; i < files.length; i++) {
            //DUGattachment_max_size_mb
            var sz = files[i].size
            names.push(files[i].name + " " + formatBytes(sz))
            isError |= (sz > DUGattachment_max_size)
            total += sz
        }
        summary.text(names.join(', '))
        if (isError) {
            summary.append("<div class='filesize'>File size cannot exceed 7MB</div>");
        }
        summary.append("<div class='filetotal'>"+total+"</div>");
        $(row_sel + ' .atadd').addClass('hidden')
        $(row_sel + ' .atdel').removeClass('hidden')
        createNewAttachmentRow()
        sanityCheck()
    })
}

$(document).ready(function() {
    $("#{{script.type_id}}").change(function() {
        onVisSelection();
    });

    onVisSelection();

    addConditional('tr.conditional', setConditional);

    addValidation('#email', validateEmail);
    addValidation('#cc', validateCC);
    addValidation('.required', toggleWarningState);
    $('tr.any').each(function() {
        var parent = $(this)
        var label = $(this).find('.compulsory')
        var childValueFn = function(f) {
            label.toggleClass('warning', parent.find('input:checkbox:checked').length == 0);
        }
        $(this).find('input.any_required').on('change keyup paste', childValueFn);
        childValueFn();
    })
    addValidation('#workflow', validatePath);

    createNewAttachmentRow()

    $('.start_visible').addClass('hidden');
    $('.start_hidden').removeClass('hidden');

    prePopulate()
    sanityCheck()
});


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getJson(url, data, successCallback, errorCallback, completeCallback) {
    $.ajax({
        dataType: "json",
        method: 'get',
        url: url,
        data: data,
        success: successCallback,
        error: errorCallback,
        complete: completeCallback
    });
}

function postJson(url, data, successCallback, errorCallback, completeCallback) {
    data['csrfmiddlewaretoken']=getCookie('csrftoken');
    $.ajax({
        dataType: "json",
        method: 'post',
        url: url,
        data: data,
        success: successCallback,
        error: errorCallback,
        complete: completeCallback
    });
}

function validate_passwords_match() {
    return $('#id_confirmPassword').val() === $('#id_password').val();
}

function getFormData($form){
    /* retorna la data del form en json*/
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};
    $.map(unindexed_array, function(n, i){
        indexed_array[n['name']] = n['value'];
    });
    return indexed_array;
}

function toTimeUnix( date, hour) {
    /*los parametros son los values de los inputs !!! */
    date = new Date(date);
    hora = hour.split(":");
    date.setHours(hora[0], hora[1]);
    return date.getTime() / 1000;
}


function insert_user_data(data_user){
    $("#fname").html("Nombre:  " + data_user.nombre);
    $("#lname").html("Apellido:  " + data_user.apellido);
    $("#dni").html("DNI:  " + data_user.dni);
    $("#email").html("E-mail:  " + data_user.mail);
    $("#birthday").html("Fecha de nacimiento:  " + data_user.fecha_de_nacimiento);
}

function insert_credit_card_data(data) {

    var card = data.get_tarjetas_de_credito;
    if (card !== null){
        for (i = 0; i < card.length; i++) {
            output = '';
            output += '<div id="card_' + i + '"> Tarjeta ' + i + '</div>';
            output += '<p> Fecha de vencimiento:  ' + card[i].fecha_de_vencimiento + '</p>';
            output += '<p> Numero de tarjeta:  ' + card[i].numero + '</p>';
            output += '<hr>';
            $("#tarjetas").append(output);
        }
    }
}

function insert_cuenta_bancaria_data(data) {
    var cbu = data.get_cuentas_bancarias;
    if (cbu !== null){
        for (i=0; i < cbu.length; i++){
            output='';
            output += '<div id="cbu_' + i +'"> Cuenta ' + i + '</div>';
            output += '<p> Entidad:  '+cbu[i].entidad+'</p>';
            output += '<p> CBU:  '+cbu[i].cbu+'</p>';
            $("#cuentas_bancarias").append(output)
        }
    }
}

function trigger_modal_agregar(id){
    $(id).modal('show');
}


function trigger_modal_modificar_usuario(datos) {
    $("#modal_fname").val(datos.usuario.nombre);
    $("#modal_lname").val(datos.usuario.apellido);
    $("#modal_dni").val(datos.usuario.dni);
    $("#modal_email").val(datos.usuario.mail);
    $("#modal_brithday").html('<input id="modal_brithday" class="form-control" type="date" required name="birthDay" value="'+datos.usuario.fecha_de_nacimiento+'">');
    $("#id_info_user").modal('show');
}

function showElement(id) {
    $(id).toggle(300);
}
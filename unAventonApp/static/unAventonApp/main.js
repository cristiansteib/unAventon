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
    data['csrfmiddlewaretoken'] = getCookie('csrftoken');
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

function getFormData($form) {
    /* retorna la data del form en json*/
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};
    $.map(unindexed_array, function (n, i) {
        indexed_array[n['name']] = n['value'];
    });
    return indexed_array;
}

function toTimeUnix(date, hour) {
    /*los parametros son los values de los inputs !!! */
    date = new Date(date);
    hora = hour.split(":");
    date.setHours(hora[0], hora[1]);
    return date.getTime() / 1000;
}


function insert_user_data(data_user) {
    $("#fname").html(data_user.nombre);
    $("#lname").html(data_user.apellido);
    $("#dni").html("dni:  " + data_user.dni);
    $("#email").html( data_user.mail);
    $("#birthday").html("Cumplea&ntilde;os:  " + data_user.fecha_de_nacimiento);
}

function insert_credit_card_data(data) {

    var card = data.get_tarjetas_de_credito;
    if (card !== null) {
        $("#tarjetas").html('');
        for (i = 0; i < card.length; i++) {
            output = '';
            output += '<div class="card card-custom" id="tarjeta_' + i + '"> <div class="card-body">';
            output += '<h6> fecha de vencimiento:  ' + card[i].fecha_de_vencimiento + '</h6>';
            output += '<h6> fecha de creacion:  ' + card[i].fecha_de_creacion + '</h6>';
            output += '<h6> numero de tarjeta:  ' + card[i].numero + '</h6>';
            output += '<h6> CCV:  ' + card[i].ccv + '</h6>';
            output += '<input hidden name="id_tarjeta_' + i + '" value="' + card[i].id + '">';
            output += '<button type="button" class="btn" onclick="trigger_modal_modificar_tarjeta(' + i + ')">Editar datos</button> ';
            output += '<button type="button" class="btn" onclick="eliminar_tarjeta_credito(' + card[i].id + ', this)">Borrar tarjeta</button>';
            output += '</div></div>';
            $("#tarjetas").append(output);
        }
    }
}

function insert_cuenta_bancaria_data(data) {
    var cuentas = data.get_cuentas_bancarias;
    if (cuentas !== null) {
        $("#cuentas_bancarias").html('');
        for (i = 0; i < cuentas.length; i++) {
            output = '';
            output += '<div class="card card-custom" id="cuenta_' + i + '"><div class="card-body">';
            output += '<h6> entidad:  ' + cuentas[i].entidad + '</h6>';
            output += '<h6> CBU:  ' + cuentas[i].cbu + '</h6>';
            output += '<input hidden name="id_cuenta_' + i + '" value="' + cuentas[i].id + '">';
            output += '<button type="button" class="btn" onclick="trigger_modal_modificar_cuenta_bancaria(' + i + ')">Editar datos</button> ';
            output += '<button type="button" class="btn"  onclick="eliminar_cuenta_bancaria(' + cuentas[i].id +', this)" >Borrar Cuenta</button>';
            output += '</div></div>';

            $("#cuentas_bancarias").append(output);
        }
    }
}


//completar vehiculo
function insert_vehicle_data(data) {
    var autos = data.get_vehiculos;
    $("#autos").html('');
    if (autos !== null) {
        for (i = 0; i < autos.length; i++) {
            output = '';
            output += '<div class="card card-custom" id="auto_' + i + '"><div class="card-body">';
            output += '<input hidden name="id_auto_' + i + '" value="' + autos[i].id + '">';
            output += '<h6> marca:  ' + autos[i].marca + '</h6>';
            output += '<h6> modelo:  ' + autos[i].modelo + '</h6>';
            output += '<h6> capacidad:  ' + autos[i].capacidad + '</h6>';
            output += '<h6> dominio:  ' + autos[i].dominio + '</h6>';
            output += '<button type="button" class="btn" onclick="trigger_modal_modificar_vehiculo(' + i + ')">Editar datos</button> ';
            output += '<button type="button" class="btn" onclick="eliminar_auto(' + autos[i].id + ', this)">Borrar auto</button>';
            output += '</div></div>';

            $("#autos").append(output);
        }
    }
}

function trigger_modal_agregar(id) {
    $(id).modal('show');
}

function trigger_modal_modificar_usuario(datos) {
    $("#modal_fname").val(datos.usuario.nombre);
    $("#modal_lname").val(datos.usuario.apellido);
    $("#modal_dni").val(datos.usuario.dni);
    $("#modal_email").val(datos.usuario.mail);
    $("#modal_brithday").html('<input id="modal_brithday" class="form-control" type="date" required name="birthDay" value="' + datos.usuario.fecha_de_nacimiento + '">');
    $("#id_info_user").modal('show');
}

function trigger_modal_modificar_tarjeta(tarjeta) {
    d = datos.get_tarjetas_de_credito[tarjeta];
    $("#modal_id_tarjeta").val(d.id);
    $("#modal_num_tarjeta").val(d.numero);
    $("#modal_dateVto").val(d.fecha_de_vencimiento);
    $("#modal_dateCreation").val(d.fecha_de_creacion);
    $("#modal_ccv").val(d.ccv);
    $("#id_modal_modificar_tarjeta").modal('show');
}

function trigger_modal_modificar_cuenta_bancaria(cuenta) {
    d = datos.get_cuentas_bancarias[cuenta];
    $("#modal_id_cuenta").val(d.id);
    $("#modal_entidad").val(d.entidad);
    $("#modal_codigo_cbu").val(d.cbu);
    $("#id_modal_modificar_cuenta").modal('show');
}

function trigger_modal_modificar_vehiculo(auto) {
    d = datos.get_vehiculos[auto];
    $("#modal_id_auto").val(d.id);
    $("#modal_marca").val(d.marca);
    $("#modal_modelo").val(d.modelo);
    $("#modal_capacidad").val(d.capacidad);
    $("#modal_dominio").val(d.dominio);
    $("#id_modal_modificar_auto").modal('show');
}

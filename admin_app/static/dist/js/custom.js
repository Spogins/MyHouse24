let delete_image = function(csrf_token, url){
    $.ajax({
        headers: { "X-CSRFToken": csrf_token.toString() },
        type: "GET",
        url: url,
        processData: false,
        contentType: false,
        success: function(response){
            let data = JSON.parse(response)
            console.log(data);
            $('#id_hall').empty();
                                if(data.length!=0){
                                    $.each(data, function(key, value) {
                                    $('#id_hall')
                                        .append($('<option>', { value : value.pk })
                                        .text(value.fields.title));
                                });
                                }
            // code to change price in front end
        }
    });
}

$(".clickable-row").click(function(e) {
    console.log(e.target);
    if (e.target.getAttribute('class') == 'checkbox-item' || e.target.getAttribute('class') == 'custom-control-input' ||
    e.target.getAttribute('class') == 'custom-control-label'){
        return
    }
    window.location = $(this).attr("href");
    });

function get_counters(flat){
    $.ajax({
        headers: { "X-CSRFToken": '{{ csrf_token }}' },
        type: "GET",
        url: '/admin/get_counters',
        data: {'flat': flat},
        contentType: 'json/application',
        success: function(response){
            let counters = response;
            let answer = render(counters);
        },
        error: function (responce){
            console.log('error get_service');
        }
    });
}

function render(data) {
    // Рендер шаблона
    moment.locale('ru')
    $(data.counters).map(function (i, elem) {
        elem.month = moment(elem.date).format('MMMM YYYY');
        elem.date = moment(elem.date).format('DD.MM.YYYY');
    });
    let template = Hogan.compile(html);
    let output = template.render(data);

    const div = document.querySelector('.counters');
    div.innerHTML = output;
}

let html = '\
{{#counters}}\
<tr">\
      <td>{{ id }}</td>\
      <td>{{ status }}</td>\
      <td>{{ date }}</td>\
      <td>{{ month }}</td>\
      <td>{{flat__house__name}}</td>\
      <td>{{flat__section__name}}</td>\
      <td>{{flat__number}}</td>\
      <td>{{service}}</td>\
      <td>{{indication}}</td>\
      <td>{{service__unit}}</td>\
      </tr>\
                                {{/counters}}'
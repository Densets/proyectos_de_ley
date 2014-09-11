from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import redirect
from django.db.models import Q

from pdl.models import Proyecto


def index(request):
    items = get_last_items()
    return render(request, "pdl/index.html", {"items": items})


def proyecto(request, short_url):
    item = Proyecto.objects.get(short_url=short_url)
    num_proy = item.numero_proyecto
    item = prettify_item(item)
    return render(request, "pdl/proyecto.html", {'item': item, 'num_proy':
                                                 num_proy,
                                                 }
                  )


def about(request):
    return render(request, "pdl/about.html")


def search(request):
    if 'q' in request.GET:
        answer = "got query"
        query = request.GET['q']
        query = sanitize(query)
        if query.strip() == '':
            return redirect("/")
        else:
            template = loader.get_template('pdl/search.html')
            results = find_in_db(query)
        """
                context = RequestContext(request, {
                    'items': results,
                    'keyword': query,
                })
                return HttpResponse(template.render(context))
        else:
            message = "you submitted and empty form."
        context = RequestContext(request, {
            'content': message,
            'keyword': query,
        })
        return HttpResponse(template.render(context))
        """
        return render(request, "pdl/search.html", {"results": results,
                                                   "keyword": query})
    return HttpResponse("no answer")


def find_in_db(query):
    try:
        items = Proyecto.objects.filter(
            Q(short_url__icontains=query) |
            Q(codigo__icontains=query) |
            Q(numero_proyecto__icontains=query) |
            Q(titulo__icontains=query) |
            Q(pdf_url__icontains=query) |
            Q(expediente__icontains=query) |
            Q(seguimiento_page__icontains=query) |
            Q(congresistas__icontains=query),
        ).order_by('-codigo')
        if len(items) > 0:
            results = []
            for i in items:
                results.append(prettify_item(i))
        else:
            results = "No se encontraron resultados."
    except Proyecto.DoesNotExist:
        results = "No se encontraron resultados."
    return results


def sanitize(s):
    s = s.replace("'", "")
    s = s.replace('"', "")
    s = s.replace("/", "")
    s = s.replace("\\", "")
    s = s.replace(";", "")
    s = s.replace("=", "")
    s = s.replace("*", "")
    s = s.replace("%", "")
    return s


def get_last_items():
    """All items from the database are extracted as list of dictionaries."""
    items = Proyecto.objects.all().order_by('-codigo')
    pretty_items = []
    for i in items:
        pretty_items.append(prettify_item(i))
    return pretty_items


def prettify_item(item):
    out = "<p>"
    out += "<a href='/p/" + str(item.short_url)
    out += "' title='Permalink'>"
    out += "<b>" + item.numero_proyecto + "</b></a></p>\n"
    out += "<h4>" + item.titulo + "</h4>\n"
    out += "<p>" + hiperlink_congre(item.congresistas) + "</p>\n"

    if item.pdf_url != '':
        out += "<a class='btn btn-lg btn-primary'"
        out += " href='" + item.pdf_url + "' role='button'>PDF</a>\n"
    else:
        out += "<a class='btn btn-lg btn-primary disabled'"
        out += " href='#' role='button'>Sin PDF</a>\n"

    if item.expediente != '':
        out += "<a class='btn btn-lg btn-primary'"
        out += " href='" + item.expediente
        out += "' role='button'>EXPEDIENTE</a>\n"
    else:
        out += "<a class='btn btn-lg btn-primary disabled'"
        out += " href='#' role='button'>Sin EXPEDIENTE</a>\n"

    if item.seguimiento_page != '':
        out += "<a class='btn btn-lg btn-primary'"
        out += " href='" + item.seguimiento_page
        out += "' role='button'>Seguimiento</a>"
    return out


def hiperlink_congre(congresistas):
    # tries to make a hiperlink for each congresista name to its own webpage
    for name in congresistas.split("; "):
        link = "<a href='/congresista/"
        link += str(convert_name_to_slug(name))
        link += "' title='ver todos sus proyectos'>"
        link += name + "</a>"
        congresistas = congresistas.replace(name, link)
    congresistas = congresistas.replace("; ", ";\n")
    return congresistas


def convert_name_to_slug(name):
    """Takes a congresista name and returns its slug."""
    name = name.replace(",", "").lower()
    # name = name.encode("ascii", "ignore")
    name = name.split(" ")

    if len(name) > 2:
        i = 0
        slug = ""
        while i < 3:
            slug += name[i]
            if i < 2:
                slug += "_"
            i += 1
        return slug + "/"

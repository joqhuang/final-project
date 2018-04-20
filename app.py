from flask import Flask, render_template, request
import model

app = Flask(__name__)

@app.route('/')
def index():
    return '''To search the database, just add the keyword to the url itself.
    For example, to search 'Kowloon', go to <a href="/Kowloon">http://127.0.0.1:5000/Kowloon</a>'''

@app.route('/<keyword>', methods=['GET','POST'])
def search(keyword):
    entities_obj_list = model.generate_entities_list(keyword)
    if len(entities_obj_list) == 0:
        return render_template("noresults.html", keyword = keyword)
    else:
        if request.method == 'POST':
            sortby = request.form['sortby']
            sortorder = request.form['sortorder']
            entities = model.get_sorted_objects(entities_obj_list, sortby, sortorder)
        else:
            entities = model.get_sorted_objects(entities_obj_list)
        return render_template("results.html", entities = entities, keyword = keyword)

@app.route('/<keyword>/<id>')
def links(keyword, id):
    entities_obj_list = model.generate_entities_list(keyword)
    for obj in entities_obj_list:
        if str(obj.id) == id:
            label = obj.label
            url = obj.url
            subjects = obj.subjects
            if len(subjects) > 0:
                return render_template("links.html",
                    keywordurl = url,
                    title = label,
                    subject_list = subjects,
                    keyword = keyword)
            else:
                return render_template("nolinks.html",
                    title = label,
                    keyword = keyword,
                    var="links")

@app.route('/<keyword>/graph')
def graph(keyword):
    model.graph_links(keyword)
    return '<h3>Return to main results for <a href="/{}">{}</a></h3>'.format(keyword, keyword)


@app.route('/<keyword>/map')
def map(keyword):
    entities_obj_list = model.generate_entities_list(keyword)
    coordinates_dict = {}
    for ent in entities_obj_list:
        try:
            label = ent.label
            lat = ent.lat
            lon = ent.lon
            coordinates_dict[label] = {"lat":lat, "lon":lon}
        except:
            pass
    if len(coordinates_dict) == 0:
        return render_template("nolinks.html",
            keyword=keyword,
            title = keyword,
            var="locations")
    else:
        model.graph_locations(coordinates_dict)
        return '<h3>Return to main results for <a href="/{}">{}</a></h3>'.format(keyword, keyword)

if __name__ == '__main__':
    app.run(debug=True)

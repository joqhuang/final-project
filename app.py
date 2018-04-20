from flask import Flask, render_template, request
import model

app = Flask(__name__)

@app.route('/<keyword>', methods=['GET','POST'])
def index(keyword):
    entities_obj_list = model.generate_entities_list(keyword)
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
        if obj.id == id:
            obj_label = obj.label
            subjects = obj.subjects
            if len(subjects) > 0:
                return render_template("links.html",
                    title = obj_label,
                    subject_list = subjects,
                    keyword = keyword)
            else:
                return render_template("nolinks.html", title=obj_label, keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True)

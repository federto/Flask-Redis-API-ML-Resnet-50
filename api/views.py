import os, csv, settings, utils, ast

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    abort
)
from middleware import model_predict
from werkzeug.datastructures import FileStorage

router = Blueprint("app_router", __name__, template_folder="templates")


@router.route("/", methods=["GET", "POST"])
def index():
    """
    GET: Index endpoint, renders our HTML code.

    POST: Used in our frontend so we can upload and show an image.
    When it receives an image from the UI, it also calls our ML model to
    get and display the predictions.
    """
    if request.method == "GET":
        return render_template("index.html")

    if request.method == "POST":
        # No file received, show basic UI
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        # File received but no filename is provided, show basic UI
        file = request.files["file"]
        if file.filename == "":
            flash("No image selected for uploading")
            return redirect(request.url)

        # File received and it's an image, we must show it and get predictions
        if file and utils.allowed_file(file.filename):
            # In order to correctly display the image in the UI and get model
            # predictions you should implement the following:
            #   1. Get an unique file name using utils.get_file_hash() function
            #   2. Store the image to disk using the new name
            #   3. Send the file to be processed by the `model` service
            #      Hint: Use middleware.model_predict() for sending jobs to model
            #            service using Redis.
            #   4. Update `context` dict with the corresponding values
            # TODO

            # 1. Get an unique file name using
            path_file = os.path.join(settings.UPLOAD_FOLDER, file.filename)
            file.save(path_file)

            with open(path_file, "rb") as fp:
                file = FileStorage(fp)

            hashed_filename = utils.get_file_hash(file)

            # 2. Store the image to disk using the new name
            path_new_file = os.path.join(settings.UPLOAD_FOLDER, hashed_filename)
            os.rename(path_file, path_new_file)

            # 3. Send the file to be processed by the `model` service
            prediction, score = model_predict(hashed_filename)

            # 4. Update `context` dict with the corresponding values
            context = {
                "prediction": prediction,
                "score": str(score),
                "filename": hashed_filename,
            }

            # Update `render_template()` parameters as needed
            # TODO

            return render_template("index.html", filename=path_new_file, context=context)
        # File received and but it isn't an image
        else:
            flash("Allowed image types are -> png, jpg, jpeg, gif")
            return redirect(request.url)


@router.route("/display/<filename>")
def display_image(filename):
    """
    Display uploaded image in our UI.
    """
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


@router.route("/predict", methods=["POST"])
def predict():
    """
    Endpoint used to get predictions without need to access the UI.

    Parameters
    ----------
    file : str
        Input image we want to get predictions from.

    Returns
    -------
    flask.Response
        JSON response from our API having the following format:
            {
                "success": bool,
                "prediction": str,
                "score": float,
            }

        - "success" will be True if the input file is valid and we get a
          prediction from our ML model.
        - "prediction" model predicted class as string.
        - "score" model confidence score for the predicted class as float.
    """
    # To correctly implement this endpoint you should:
    #   1. Check a file was sent and that file is an image
    #   2. Store the image to disk
    #   3. Send the file to be processed by the `model` service
    #      Hint: Use middleware.model_predict() for sending jobs to model
    #            service using Redis.
    #   4. Update and return `rpse` dict with the corresponding values
    # If user sends an invalid request (e.g. no file provided) this endpoint
    # should return `rpse` dict with default values HTTP 400 Bad Request code
    # TODO
    rpse = {"success": False, "prediction": None, "score": None}

    if "file" not in request.files:
        flash("No file part")
        return rpse, 400

    # File received but no filename is provided, show basic UI
    file = request.files["file"]
    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(request.url)

    # File received and it's an image, we must show it and get predictions
    if file and utils.allowed_file(file.filename):

        # get an unique file name using get_file_hash
        path_file = os.path.join(settings.UPLOAD_FOLDER, file.filename)
        file.save(path_file)
        with open(path_file, "rb") as fp:
            file = FileStorage(fp)
        hashed_filename = utils.get_file_hash(file)

        # store the image to disk using the new name
        path_new_file = os.path.join(settings.UPLOAD_FOLDER, hashed_filename)
        os.rename(path_file, path_new_file)

        # send the file to be processed by the `model` service
        prediction, score = model_predict(hashed_filename)

        # update response dict with the corresponding values
        rpse = {
            "success": True,
            "prediction": prediction,
            "score": float(score),
        }

        return jsonify(rpse)


        # File received and but it isn't an image
    else:
        flash("Allowed image types are -> png, jpg, jpeg, gif")
        return redirect(request.url)



    return jsonify(rpse)



@router.route("/feedback", methods=["GET", "POST"])
def feedback():
    """
    Store feedback from users about wrong predictions on a plain text file.

    Parameters
    ----------
    report : request.form
        Feedback given by the user with the following JSON format:
            {
                "filename": str,
                "prediction": str,
                "score": float
            }

        - "filename" corresponds to the image used stored in the uploads
          folder.
        - "prediction" is the model predicted class as string reported as
          incorrect.
        - "score" model confidence score for the predicted class as float.
    """
    report = request.form.get("report")

    if not report:
        return "No data", 200

    # Store the reported data to a file on the corresponding path
    # already provided in settings.py module
    # TODO

    with open(settings.FEEDBACK_FILEPATH, 'a') as csv_file:
        csv_file.write(report + "\n")
    csv_file.close()

    return render_template("index.html")

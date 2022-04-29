import os
import uuid
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from werkzeug.utils import secure_filename
from app import current_app, db
from app.main.forms import EditProfileForm, PostForm, CommentForm, HottopicForm, EditHottopicForm, JournalForm, \
    Did_you_knowForm, Other_projectsForm, CategoriesForm, ContactForm, NewsForm, QuizForm, RandomForm, CurrentForm, \
    AboutForm
from app.models import User, Post, Comment, HotTopic, Journal, Did_you_know, Other_projects, Categories, Contact_Us, \
    News, Quiz, About, Current, Random
from app.main import bp
from config import Config


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
def Home():
    return render_template('Home.html', title="Home")


@bp.route('/post/<int:id>', methods=['GET', 'POST'])
def post_page(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(comment=form.comment.data,
                          comment_username=current_user.username,
                          post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('main.post_page', id=id))
    page = request.args.get('page', 1, type=int)
    # list the corresponding comment in post
    comments = Comment.query.filter_by(post_id=post.id)
    pages = comments.paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.post_page', page=comments.next_num) \
        if pages.has_next else None
    prev_url = url_for('main.post_page', page=comments.prev_num) \
        if pages.has_prev else None
    return render_template('post.html', title=_('post comment'), form=form, post=post,
                           comments=comments, next_url=next_url,
                           prev_url=prev_url, pages=pages.items)



@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            body=form.body.data,
            author=current_user,)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('userHome'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        flash(_('Post has been updated'))
        return redirect(url_for('main.post_page', id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.body.data = post.body
    return render_template('edit_post.html', title=_('Edit Profile'),
                           form=form, post=post)


@bp.route('/delete_post/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post_to_delete = Post.query.filter_by(id=id).first()
    del_po_com = Comment.query.filter_by(post_id=id).first()
    db.session.delete(post_to_delete)
    if del_po_com is not None:
        db.session.delete(del_po_com)
        db.session.commit()
    else:
        db.session.commit()
        flash(_('Post was deleted'))
        return redirect(url_for('main.explore'))
    return redirect(url_for('main.explore'))


@bp.route('/delete_comment/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    com_to_del = Comment.query.filter_by(comment_id=comment_id).first()
    db.session.delete(com_to_del)
    db.session.commit()
    flash(_('Comment was deleted'))
    return redirect(url_for('main.explore'))


@bp.route('/upload_hottopic', methods=['GET', 'POST'])
@login_required
def upload_hottopic():
    form = HottopicForm()
    if request.method == 'POST':
        file = request.files['Upload Image']
        if file.filename == '':
            flash('No file was selected')
            return redirect(url_for('main.upload_hottopic'))
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            db.session.commit()
            hottopic = HotTopic(description=form.description.data,
                                title=form.title.data,
                                exlink=form.title.data,
                                author=current_user,
                                image_name=filename)

            db.session.add(hottopic)
            db.session.commit()
            flash('Image has been successfully uploaded')
            return redirect(url_for('main.hottopic'))
        else:
            flash('Allowed media types are - png, jpg, jpeg, gif')
            return redirect(url_for('main.hottopic'))
    else:
        return render_template('upload_hottopic.html', title=_('Hot topic'), form=form)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@bp.route('/hot-topic', methods=['GET', 'POST'])
def hottopic():
    page = request.args.get('page', 1, type=int)
    hottopics = HotTopic.query.order_by(HotTopic.id.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('hot_topic.html', title=_('Hot topic'), hottopics=hottopics.items)


@bp.route('/edit_hot/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_hottopic(id):
    hottopic = HotTopic.query.get_or_404(id)
    form = EditHottopicForm()
    if request.method == 'POST':
        file = request.files['Upload Image']
        if file.filename == '':
            hottopic.title = form.title.data
            hottopic.description = form.description.data
            hottopic.exlink = form.exlink.data
            db.session.commit()
            flash(_('Post has been updated'))
            return redirect(url_for('main.hottopic'))
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            hottopic.title = form.title.data
            hottopic.description = form.description.data
            hottopic.exlink = form.exlink.data
            hottopic.image_name = filename
            db.session.commit()
            flash(_('Post has been updated'))
            return redirect(url_for('main.hottopic'))
    elif request.method == 'GET':
        form.title.data = hottopic.title
        form.description.data = hottopic.description
        form.exlink.data = hottopic.exlink
    return render_template('edit_hottopic.html', title=_('Edit Hottopic'),
                           form=form, hottopic=hottopic, id=hottopic.id)


@bp.route('/del_hot/<int:id>', methods=['GET', 'POST'])
@login_required
def del_hot(id):
    HT_to_delete = HotTopic.query.get_or_404(id)
    db.session.delete(HT_to_delete)
    db.session.commit()
    flash(_('Hot Topic was deleted'))
    return redirect(url_for('main.hottopic'))


@bp.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    form = JournalForm()
    if form.validate_on_submit():
        journal = Journal(date=form.date.data,
                          issue=form.issue.data,
                          user_id=current_user.id)
        db.session.add(journal)
        db.session.commit()
        return redirect(url_for('main.journal', id=id))
    page = request.args.get('page', 1, type=int)
    journals = Journal.query.order_by(Journal.id.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('Journal.html', title=_('Journal'), form=form, journals=journals.items)


@bp.route('/edit_journal/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_journal(id):
    journal = Journal.query.get_or_404(id)
    form = JournalForm()
    if form.validate_on_submit():
        journal.date = form.date.data
        journal.issue = form.issue.data
        db.session.commit()
        flash(_('journal has been updated'))
        return redirect(url_for('main.journal'))
    elif request.method == 'GET':
        form.date.data = journal.date
        form.issue.data = journal.issue
    return render_template('edit_journal.html', title=_('Edit journal'),
                           form=form, journal=journal, id=journal.id)


@bp.route('/del_journal/<int:id>', methods=['GET', 'POST'])
@login_required
def del_journal(id):
    journal_to_delete = Journal.query.get_or_404(id)
    db.session.delete(journal_to_delete)
    db.session.commit()
    flash(_('journal was deleted'))
    return redirect(url_for('main.journal'))

@bp.route('/Did_you_know', methods=['GET', 'POST'])
@login_required
def Did_you_knows():
    form = Did_you_knowForm()
    if form.validate_on_submit():
        did_you_know = Did_you_know(topic=form.topic.data,
                                    user_id=current_user.id)
        db.session.add(did_you_know)
        db.session.commit()
        return redirect(url_for('main.Did_you_knows', id=did_you_know.id))
    page = request.args.get('page', 1, type=int)
    dyk = Did_you_know.query.order_by(Did_you_know.id.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('Did_you_know.html', title=_('Did_you_know'), form=form, dyk=dyk.items)

@bp.route('/edit_Did_you_know/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_Did_you_know(id):
    dyk = Did_you_know.query.get_or_404(id)
    form = Did_you_knowForm()
    if form.validate_on_submit():
        dyk.topic = form.topic.data
        dyk.date = form.date.data
        dyk.content = form.content.data
        db.session.commit()
        flash(_('Did_you_know has been updated'))
        return redirect(url_for('main.Did_you_knows'))
    elif request.method == 'GET':
        form.topic.data = dyk.topic
        form.date.data = dyk.date
        form.content.data = dyk.content
    return render_template('edit_Did_you_know.html', title=_('Edit Did_you_know'),
                           form=form, dyk=dyk, topic=dyk.topic)

@bp.route('/del_Did_you_know/<int:id>', methods=['GET', 'POST'])
@login_required
def del_Did_you_know(id):
    dyk_to_delete = Did_you_know.query.get_or_404(id)
    db.session.delete(dyk_to_delete)
    db.session.commit()
    flash(_('Did you know topic was deleted'))
    return redirect(url_for('main.Did_you_knows'))

@bp.route('/Other_projects', methods=['GET', 'POST'])
@login_required
def Other_project():
    form = Other_projectsForm()
    if form.validate_on_submit():
        op = Other_projects(Pname=form.Pname.data,
                          description=form.description.data,
                          user_id=current_user.id)
        db.session.add(op)
        db.session.commit()
        return redirect(url_for('main.Other_project', id=op.id))
    page = request.args.get('page', 1, type=int)
    opp = Other_projects.query.order_by(Other_projects.id.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('Other_projects.html', title=_('Other projects'), form=form, opp=opp.items)

@bp.route('/edit_Other_projects/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_Other_projects(id):
    op = Other_projects.query.get_or_404(id)
    form = Other_projectsForm()
    if form.validate_on_submit():
        op.Pname = form.Pname.data
        op.description = form.description.data
        db.session.commit()
        flash(_('Other projects name has been updated'))
        return redirect(url_for('main.Other_project'))
    elif request.method == 'GET':
        form.Pname.data = op.Pname
        form.description.data = op.description
    return render_template('edit_Other_projects.html', title=_('Edit Other_projects'),
                           form=form, op=op, Pname=op.Pname)

@bp.route('/del_Other_projects/<int:id>', methods=['GET', 'POST'])
@login_required
def del_Other_projects(id):
    op_delete = Other_projects.query.get_or_404(id)
    db.session.delete(op_delete)
    db.session.commit()
    flash(_('Other projects name  was deleted'))
    return redirect(url_for('main.Other_project'))

@bp.route('/Categories', methods=['GET', 'POST'])
@login_required
def Categories1():
    form = CategoriesForm()
    if form.validate_on_submit():
        cs = Categories(category=form.category.data,
                          content=form.content.data,
                          user_id=current_user.id)
        db.session.add(cs)
        db.session.commit()
        return redirect(url_for('main.Categories1', id=cs.id))
    page = request.args.get('page', 1, type=int)
    cy = Categories.query.order_by(Categories.category.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('Categories.html', title=_('Categories'), form=form, cy=cy.items)


@bp.route('/edit_Categories/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_Categories(id):
    cs = Categories.query.get_or_404(id)
    form = CategoriesForm()
    if form.validate_on_submit():
        cs.category = form.category.data
        cs.content = form.content.data
        db.session.commit()
        flash(_('Categories has been updated'))
        return redirect(url_for('main.Categories1'))
    elif request.method == 'GET':
        form.category.data = cs.category
        form.content.data = cs.content
    return render_template('edit_Categories.html', title=_('Edit Categories'),
                           form=form, cs=cs, category=cs.category)


@bp.route('/del_Categories/<int:id>', methods=['GET', 'POST'])
@login_required
def del_Categories(id):
    Categories_to_delete = Categories.query.get_or_404(id)
    db.session.delete(Categories_to_delete)
    db.session.commit()
    flash(_('category was deleted'))
    return redirect(url_for('main.Categories1'))

@bp.route('/contact_us', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact = Contact_Us(details=form.details.data,
                             title=form.title.data,
                             user_id=current_user.id,
                             contact_username=current_user.username)

        db.session.add(contact)
        db.session.commit()
        flash('Your request has benn sent.')
        return redirect(url_for('main.contact'))
    return render_template('contact_us.html', title=_('Contact Us'), form=form)

@bp.route('/news', methods=['GET', 'POST'])
def news():
    page = request.args.get('page', 1, type=int)
    news = News.query.order_by(News.id.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('news.html', title=_('News'), news=news.items)

@bp.route('/upload_news', methods=['GET', 'POST'])
@login_required
def upload_news():
    form = NewsForm()
    if form.validate_on_submit():
        news = News(title=form.title.data,
                    details=form.details.data,
                    date=form.date.data,
                    user_id=current_user.id,
                    url=form.url.data)

        db.session.add(news)
        db.session.commit()
        flash('News has benn uploaded')
        return redirect(url_for('main.news'))
    return render_template('upload_news.html', title=_('Upload News'), form=form)

@bp.route('/edit_news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    news = News.query.get_or_404(id)
    form = NewsForm()
    if form.validate_on_submit():
        news.date = form.date.data
        news.title = form.title.data
        news.details = form.details.data
        news.url = form.url.data
        db.session.commit()
        flash(_('News has been updated.'))
        return redirect(url_for('main.news'))
    elif request.method == 'GET':
        form.date.data = news.date
        form.title.data = news.title
        form.details.data = news.details
        form.url.data = news.url
    return render_template('edit_news.html', title=_('Edit News'),
                           form=form, news=news, id=news.id)

@bp.route('/del_news/<int:id>', methods=['GET', 'POST'])
@login_required
def del_news(id):
    news_to_delete = News.query.get_or_404(id)
    db.session.delete(news_to_delete)
    db.session.commit()
    flash(_('News has benn deleted.'))
    return redirect(url_for('main.news'))

@bp.route('/quiz', methods=['GET', 'POST'])
def quiz():
    page = request.args.get('page', 1, type=int)
    quiz = Quiz.query.order_by(Quiz.id.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('quiz.html', title=_('Quiz'), quiz=quiz.items)

@bp.route('/upload_quiz', methods=['GET', 'POST'])
@login_required
def upload_quiz():
    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(question=form.question.data,
                    answer=form.answer.data,
                    user_id=current_user.id,
                    username=current_user.username)

        db.session.add(quiz)
        db.session.commit()
        flash('Your quiz has benn uploaded')
        return redirect(url_for('main.quiz'))
    return render_template('upload_quiz.html', title=_('Upload Quiz'), form=form)

@bp.route('/edit_quiz/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    form = QuizForm()
    if form.validate_on_submit():
        quiz.question = form.question.data
        quiz.answer = form.answer.data
        db.session.commit()
        flash(_('Quiz has been updated.'))
        return redirect(url_for('main.quiz'))
    elif request.method == 'GET':
        form.question.data = quiz.question
        form.answer.data = quiz.answer
    return render_template('edit_quiz.html', title=_('Edit Quiz'),
                           form=form, quiz=quiz, id=quiz.id)

@bp.route('/del_quiz/<int:id>', methods=['GET', 'POST'])
@login_required
def del_quiz(id):
    quiz_to_delete = Quiz.query.get_or_404(id)
    db.session.delete(quiz_to_delete)
    db.session.commit()
    flash(_('Quiz has benn deleted.'))
    return redirect(url_for('main.quiz'))

@bp.route('/about', methods=['GET', 'POST'])
def about():
    page = request.args.get('page', 1, type=int)
    about = About.query.order_by(About.id.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('about.html', title=_('About'), about=about.items)

@bp.route('/upload_about', methods=['GET', 'POST'])
@login_required
def upload_about():
    form = AboutForm()
    if form.validate_on_submit():
        about = About(title=form.title.data,
                    details=form.details.data,
                    date=form.date.data,
                    user_id=current_user.id)

        db.session.add(about)
        db.session.commit()
        flash('About has been uploaded')
        return redirect(url_for('main.about'))
    return render_template('upload_about.html', title=_('Upload About'), form=form)

@bp.route('/edit_about/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_about(id):
    about = About.query.get_or_404(id)
    form = AboutForm()
    if form.validate_on_submit():
        about.date = form.date.data
        about.title = form.title.data
        about.details = form.details.data
        db.session.commit()
        flash(_('About has been updated.'))
        return redirect(url_for('main.about'))
    elif request.method == 'GET':
        form.date.data = about.date
        form.title.data = about.title
        form.details.data = about.details
    return render_template('edit_about.html', title=_('Edit About'),
                           form=form, about=about, id=about.id)

@bp.route('/del_about/<int:id>', methods=['GET', 'POST'])
@login_required
def del_about(id):
    about_to_delete = About.query.get_or_404(id)
    db.session.delete(about_to_delete)
    db.session.commit()
    flash(_('About has been deleted.'))
    return redirect(url_for('main.about'))

@bp.route('/current', methods=['GET', 'POST'])
def current():
    page = request.args.get('page', 1, type=int)
    current = Current.query.order_by(Current.id.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('current.html', title=_('Current'), current=current.items)

@bp.route('/upload_Current', methods=['GET', 'POST'])
@login_required
def upload_current():
    form = CurrentForm()
    if form.validate_on_submit():
        current = Current(title=form.title.data,
                    details=form.details.data,
                    date=form.date.data,
                    user_id=current_user.id)

        db.session.add(current)
        db.session.commit()
        flash('Current has been uploaded')
        return redirect(url_for('main.current'))
    return render_template('upload_current.html', title=_('Upload Current'), form=form)

@bp.route('/edit_current/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_current(id):
    current = Current.query.get_or_404(id)
    form = CurrentForm()
    if form.validate_on_submit():
        current.date = form.date.data
        current.title = form.title.data
        current.details = form.details.data
        db.session.commit()
        flash(_('Current has been updated.'))
        return redirect(url_for('main.current'))
    elif request.method == 'GET':
        form.title.data = current.title
        form.details.data = current.details
        form.date.data = current.date
    return render_template('edit_current.html', title=_('Edit Current'),
                           form=form, current=current, id=current.id)

@bp.route('/del_Current/<int:id>', methods=['GET', 'POST'])
@login_required
def del_current(id):
    current_to_delete = Current.query.get_or_404(id)
    db.session.delete(current_to_delete)
    db.session.commit()
    flash(_('Current has been deleted.'))
    return redirect(url_for('main.current'))

@bp.route('/random', methods=['GET', 'POST'])
def random():
    page = request.args.get('page', 1, type=int)
    random = Random.query.order_by(Random.id.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('random.html', title=_('Random'), random=random.items)

@bp.route('/upload_random', methods=['GET', 'POST'])
@login_required
def upload_random():
    form = RandomForm()
    if form.validate_on_submit():
        random = Random(title=form.title.data,
                    details=form.details.data,
                    user_id=current_user.id,
                    username=current_user.username)

        db.session.add(random)
        db.session.commit()
        flash('Random has been uploaded')
        return redirect(url_for('main.random'))
    return render_template('upload_random.html', title=_('Upload Random'), form=form)

@bp.route('/edit_random/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_random(id):
    random = Random.query.get_or_404(id)
    form = RandomForm()
    if form.validate_on_submit():
        random.title = form.title.data
        random.details = form.details.data
        db.session.commit()
        flash(_('Random has been updated.'))
        return redirect(url_for('main.random'))
    elif request.method == 'GET':
        form.title.data = random.title
        form.details.data = random.details
    return render_template('edit_random.html', title=_('Edit Random'),
                           form=form, random=random, id=random.id)

@bp.route('/del_random/<int:id>', methods=['GET', 'POST'])
@login_required
def del_random(id):
    random_to_delete = Random.query.get_or_404(id)
    db.session.delete(random_to_delete)
    db.session.commit()
    flash(_('Random has been deleted.'))
    return redirect(url_for('main.random'))
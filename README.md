# OSSWire

A FastAPI-based web application similar to Hacker News, focused on open source software news and discussion.

## Features

- **User Authentication**: Register, login, and logout with session-based authentication
- **Post Submissions**: Submit links or text posts with required license metadata
- **Voting System**: Upvote/downvote posts and comments
- **Threaded Comments**: Nested comment system with replies
- **Filtering & Sorting**: Filter by license, date range, minimum score, and sort by latest/top
- **License Metadata**: Every submission must have a license (MIT, Apache-2.0, GPL-3.0, etc.)
- **Clean UI**: Hacker News-inspired interface with responsive design

## Tech Stack

- **Backend**: FastAPI with Python 3.7+
- **Database**: SQLite with SQLAlchemy ORM
- **Templates**: Jinja2
- **Authentication**: JWT tokens with bcrypt password hashing
- **Styling**: Custom CSS (Hacker News inspired)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd osswire
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the seed script** to populate the database with test data:
   ```bash
   python seed.py
   ```

4. **Start the application**:
   ```bash
   uvicorn main:app --reload
   ```

5. **Access the application** at `http://localhost:8000`

## Test Users

The seed script creates the following test users (password: `password123`):
- `alice@example.com` / `alice`
- `bob@example.com` / `bob`
- `charlie@example.com` / `charlie`
- `diana@example.com` / `diana`

## Project Structure

```
osswire/
├── main.py                 # FastAPI application entry point
├── models.py              # SQLAlchemy models
├── database.py            # Database configuration
├── auth.py                # Authentication utilities
├── seed.py                # Database seeding script
├── requirements.txt       # Python dependencies
├── routes/                # Route modules
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   ├── submissions.py    # Post submission routes
│   └── comments.py       # Comment routes
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template
│   ├── home.html         # Homepage
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── submit.html       # Post submission page
│   ├── post.html         # Individual post view
│   └── comment.html      # Comment template
└── static/               # Static files (CSS, JS, images)
```

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Login form submission
- `GET /register` - Registration page
- `POST /register` - Registration form submission
- `GET /logout` - Logout

### Posts
- `GET /` - Homepage with post listings and filters
- `GET /submit` - Post submission page
- `POST /submit` - Submit new post
- `GET /post/{post_id}` - View individual post with comments
- `POST /vote/{post_id}` - Vote on post

### Comments
- `POST /comment/{post_id}` - Add comment to post
- `POST /vote/comment/{comment_id}` - Vote on comment

## Database Schema

### Users
- `id` (UUID, primary key)
- `username` (unique)
- `email` (unique)
- `password_hash`
- `created_at`
- `last_login`

### Posts
- `id` (UUID, primary key)
- `title`
- `url` (optional)
- `content` (optional)
- `license` (enum: MIT, Apache-2.0, GPL-3.0, BSD-3, etc.)
- `created_by` (FK to users)
- `created_at`
- `updated_at`
- `points`

### Comments
- `id` (UUID, primary key)
- `submission_id` (FK to posts)
- `parent_id` (FK to comments, nullable for replies)
- `content`
- `created_by` (FK to users)
- `created_at`
- `updated_at`
- `points`

### Votes
- `id` (UUID, primary key)
- `user_id` (FK to users)
- `post_id` (FK to posts, nullable)
- `comment_id` (FK to comments, nullable)
- `vote_type` (1 for upvote, -1 for downvote)
- `created_at`

## Features in Detail

### License System
Every submission must have a license from the predefined list:
- MIT
- Apache-2.0
- GPL-3.0
- BSD-3
- ISC
- Unlicense
- CC0
- CC-BY-4.0
- CC-BY-SA-4.0

### Filtering Options
- **License**: Filter posts by specific license type
- **Date Range**: Last day, week, or month
- **Minimum Score**: Show only posts with score above threshold
- **Sorting**: Latest first or top posts first

### Comment System
- Threaded comments with unlimited nesting
- Reply functionality for authenticated users
- Voting on comments
- Tree-style display with indentation

### Voting System
- Upvote/downvote posts and comments
- Users can change their votes
- Points are calculated and displayed
- Vote buttons are only shown to authenticated users

## Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Reset
To reset the database and reseed:
```bash
# Option 1: Manual reset
rm osswire.db
python seed.py

# Option 2: Use the reset script
python reset_db.py
```

### Adding New License Types
Edit `models.py` and add new values to the `LicenseType` enum.

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Session management with secure cookies
- Input validation and sanitization
- SQL injection protection via SQLAlchemy ORM

## Future Enhancements

- User profiles and avatars
- Post categories/tags
- Search functionality
- Email notifications
- API rate limiting
- Admin panel
- Mobile-responsive design improvements
- Dark mode theme
- RSS feeds
- Social sharing

## License

This project is open source and available under the MIT License. 
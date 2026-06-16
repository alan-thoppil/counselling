# Implementation Plan - Admin Dashboard and Content Management Capabilities

This plan outlines the enhancements to create a dedicated Admin Dashboard allowing administrators to manage topics/categories, upload resources (articles, videos, exercises), monitor bookings, manage users, and view system analytics.

## Proposed Changes

---

### Accounts Component

Configure the login redirection, navigation, and user management endpoints.

#### [MODIFY] [views.py](file:///c:/Users/ALAN%20TOM/Documents/acadeni_int/counselling/counseling_app/accounts/views.py)
- **`login_view`**: Add redirection for user role `'admin'` (or `is_superuser`) to the new `admin_dashboard` view.
- **`admin_dashboard` view**: Returns analytics metrics (e.g., total patient count, therapist count, bookings, articles) and renders `accounts/admin_dashboard.html`.
- **`list_users` view**: Returns a JSON list of all registered users (IDs, usernames, emails, roles, phone numbers, and active status).
- **`toggle_user_active` view**: Allows admins to toggle the `is_active` status of users.

#### [MODIFY] [urls.py](file:///c:/Users/ALAN%20TOM/Documents/acadeni_int/counselling/counseling_app/accounts/urls.py)
- Map `dashboard/admin/` to `admin_dashboard` view.
- Map `users/` to `list_users` view.
- Map `users/toggle/<int:user_id>/` to `toggle_user_active` view.

---

### Content Component

Enable admin CRUD operations for category topics and educational resources.

#### [MODIFY] [views.py](file:///c:/Users/ALAN%20TOM/Documents/acadeni_int/counselling/counseling_app/content/views.py)
- Add administrative views (restricted to superusers/admins):
  - **`create_category`**: Adds a new category (e.g. Anxiety, Depression, CBT).
  - **`delete_category`**: Deletes a category.
  - **`create_article`**: Uploads new content (Article, Video, or Exercise) with body text, category, and video URLs.
  - **`edit_article`**: Edits existing educational resources.
  - **`delete_article`**: Removes content.

#### [MODIFY] [urls.py](file:///c:/Users/ALAN%20TOM/Documents/acadeni_int/counselling/counseling_app/content/urls.py)
- Map `/content/categories/create/` to `create_category`.
- Map `/content/categories/delete/<int:category_id>/` to `delete_category`.
- Map `/content/articles/create/` to `create_article`.
- Map `/content/articles/edit/<int:article_id>/` to `edit_article`.
- Map `/content/articles/delete/<int:article_id>/` to `delete_article`.

---

### Templates Component

Create a unified premium admin dashboard UI matching MindWell's existing style guidelines.

#### [NEW] [admin_dashboard.html](file:///c:/Users/ALAN%20TOM/Documents/acadeni_int/counselling/counseling_app/accounts/templates/accounts/admin_dashboard.html)
A Glassmorphic page with key administrative panels separated by tabs:
1. **Analytics Dashboard Panel**: Displays metric counters (total patients, therapists, bookings, articles) in glowing cards.
2. **User Management Panel**: Lists all patients and therapists. Provides a button to toggle user activation state.
3. **Topics & Educational Resources Panel**:
   - Manage categories: Add/delete topics (Anxiety, Depression, CBT).
   - Manage articles, videos, and exercises: Lists all published contents. Includes forms to upload new resource content (Article text, YouTube video URLs, self-care exercises) and delete existing entries.
4. **All Bookings Panel**: Lists all appointments in the system (patient, therapist, date, time, and current status: pending, confirmed, completed, cancelled).

#### [MODIFY] [base.html](file:///c:/Users/ALAN%20TOM/Documents/acadeni_int/counselling/counseling_app/accounts/templates/accounts/base.html)
- Add a dashboard navigation link to `/accounts/dashboard/admin/` when logged in as an admin or superuser.

---

## Verification Plan

### Automated Tests
Run django tests to verify no breakage of authentication, appointments, and mood tracking APIs:
```powershell
venv\Scripts\python.exe manage.py test
```

### Manual Verification
1. Log in as an administrator (e.g. create a superuser if not exists via `python manage.py createsuperuser` or assign `role='admin'` to a user).
2. Verify redirect to the Admin Dashboard upon login.
3. Navigate to **User Management** and test toggling user active/inactive state.
4. Navigate to **Topics & Educational Resources**:
   - Create a category (e.g., "CBT Essentials"). Delete a test category.
   - Upload a resource of type `article` (e.g., "Anxiety Grounding Guide").
   - Upload a resource of type `video` (with YouTube URL).
   - Upload a resource of type `exercise`.
5. Verify that these resources are added and appear in patient/therapist lists.
6. Verify the booking list and analytics panels populate data correctly.

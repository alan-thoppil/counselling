import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_appointment_email(appointment, action):
    """Sends email notifications for appointment activities (booking, confirmation, cancellation)"""
    subject = f"MindWell Appointment {action.capitalize()}: {appointment.date} at {appointment.time}"
    
    if action == 'booked':
        message = (
            f"Hello {appointment.patient.username},\n\n"
            f"Your appointment with Therapist {appointment.therapist.username} has been requested for "
            f"{appointment.date} at {appointment.time}.\n\n"
            f"Reason: {appointment.reason or 'None'}\n"
            f"Status: {appointment.status.capitalize()}\n\n"
            f"Thank you for choosing MindWell!\n"
            f"MindWell Support Team"
        )
    elif action == 'confirmed':
        message = (
            f"Hello {appointment.patient.username},\n\n"
            f"Your counseling appointment with Therapist {appointment.therapist.username} on "
            f"{appointment.date} at {appointment.time} has been CONFIRMED.\n\n"
            f"Professional Preparation Guidelines:\n"
            f"- Please find a quiet, private, and comfortable space free from distractions.\n"
            f"- Log in to your MindWell dashboard 5 minutes before the session starts.\n"
            f"- Ensure a stable internet connection and that your audio/video device is working properly.\n\n"
            f"If you need to reschedule or have any questions, please contact our support team at support@mindwell.com.\n\n"
            f"Thank you for choosing MindWell!\n"
            f"MindWell Support Team"
        )
    elif action == 'completed':
        message = (
            f"Hello {appointment.patient.username},\n\n"
            f"Your appointment with Therapist {appointment.therapist.username} on "
            f"{appointment.date} at {appointment.time} has been marked as COMPLETED.\n\n"
            f"Post-Session Self-Care Guidelines:\n"
            f"- Take 10-15 minutes to reflect on the insights and takeaways from today's session.\n"
            f"- Log in to your MindWell dashboard to review shared therapist feedback and clinical summaries.\n"
            f"- Continue recording your mood daily in the Mood Journal Tracker to monitor your emotional progress.\n"
            f"- Practice any breathing or grounding exercises discussed during your session.\n\n"
            f"We are here to support you on your wellness journey.\n\n"
            f"Warm regards,\n"
            f"MindWell Support Team"
        )
    elif action == 'cancelled':
        message = (
            f"Hello {appointment.patient.username},\n\n"
            f"Your appointment with Therapist {appointment.therapist.username} on "
            f"{appointment.date} at {appointment.time} has been successfully cancelled.\n\n"
            f"If this was a mistake, please visit the dashboard to schedule a new session.\n\n"
            f"Thank you,\n"
            f"MindWell Support Team"
        )
    else:
        message = (
            f"Hello {appointment.patient.username},\n\n"
            f"Your appointment status with Therapist {appointment.therapist.username} is now "
            f"updated to '{appointment.status.capitalize()}'.\n\n"
            f"MindWell Support Team"
        )

    recipient_list = []
    if appointment.patient.email:
        recipient_list.append(appointment.patient.email)
    if appointment.therapist.email:
        recipient_list.append(appointment.therapist.email)

    if not recipient_list:
        # Fallback logging if no email addresses exist for test users
        logger.info(f"[Email simulation] No email addresses set. Log of message:\n"
                    f"Subject: {subject}\n"
                    f"Recipient List: {[appointment.patient.username, appointment.therapist.username]}\n"
                    f"Body:\n{message}\n")
        
        # Still attempt to send to default console in development to verify backend is working
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@aura.com'),
                recipient_list=['test@example.com'], # mock list to trigger print to console
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Failed to print simulated mail to console: {e}")
        return

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@aura.com'),
            recipient_list=recipient_list,
            fail_silently=True
        )
        logger.info(f"Successfully sent appointment {action} email to {recipient_list}")
    except Exception as e:
        logger.error(f"Failed to dispatch appointment email: {e}")

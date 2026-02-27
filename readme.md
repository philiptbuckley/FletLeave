# Dusty Ape Leave Tracker

This is an attempt to build a leave of absense app for Dusty Ape

## Design
It's written in python and flet so that it could potentially be 
run on a mobile app and web server for staff to interract with.

I've used an MVC design pattern to keep the code tidy. The data
is persisted in a SQLLite database currently and there is an
additional level of abstraction from the model to a repository
so that this can easily be replaced with a proper database in 
the future.

   _______         ____________      ________
  | Model |  ←→   | Repository | ←→ | SQLite |
   _______         ____________      ________
 
      ↑
 ____________  
| Controller |
 ____________  
  
      ↑

    ______
   | View |
    ______

So far it just operates a calendar and allows the user to switch
views (day/week/month/year) and select dates. A summary of all
sleected dates is displayed underneath the calendar.

Still to do:
- [ ] Implement staff
- [ ] Implement leave types
- [ ] Implement regular work days for staff so that it can rota


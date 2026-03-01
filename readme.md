# Leave Tracker

This is an attempt to build a leave of absense app for my small 
business while I learn flet at the same time

## Design
It's written in python and flet so that it could potentially be 
run on a mobile app and web server for staff to interract with.

I've used an MVC design pattern to keep the code tidy. The data
is persisted in a SQLLite database currently and there is an
additional level of abstraction from the model to a repository
so that this can easily be replaced with a proper database in 
the future.

Model   ←→    Repository  ←→  SQLite 
 
   ↑
   
Controller 
  
   ↑

  View 

It's not finished, but it works with a simple calendar and
SQLite database to persist the data. It supports multiple
employees and leave types that suit my business.

Still to do:
- [ ] Implement UK leave allowances
- [ ] Implement multiple days leave booking
- [ ] Summarise all leave for all staff
- [ ] Implement regular work days for staff so that it can rota


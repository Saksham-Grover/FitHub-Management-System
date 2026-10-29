
"""My part of the FitHub group project: managing fitness classes.

Run this file to test the class screen: py class_management.py
The main menu can call show_class_management(parent).
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from decimal import Decimal, InvalidOperation
import mysql.connector
from db_config import get_connection
from class_capacity import check_class_capacity

# I used the same dark background as the member management screen.
BG = '#2c3e50'
DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

# This helper sends SQL queries to our group database.
def query(sql, params=(), fetch=False):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        if fetch:
            return cur.fetchall()
        conn.commit()
        return cur.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


class ClassManagement:
    def __init__(self, window):
        self.window=window
        window.title('FitHub - Class Management')
        window.geometry('1100x700')
        window.configure(bg=BG)
        self.selected_id=None
        self.vars={key:tk.StringVar() for key in ['name','type','trainer','day','time','capacity','fee','search','search_by','min_fee','max_fee']}
        self.vars['day'].set(DAYS[0]); self.vars['search_by'].set('Class Name')
        self.trainers={}
        self.build()
        self.load_trainers()
        self.load_classes()

    def build(self):
        form=tk.LabelFrame(self.window,text=' Class Details ',bg=BG,fg='white',padx=12,pady=10)
        form.pack(fill='x',padx=12,pady=12)
        fields=[('Class Name','name'),('Class Type','type'),('Trainer','trainer'),('Day','day'),('Start Time (HH:MM)','time'),('Capacity','capacity'),('Fee ($)','fee')]
        for i,(label,key) in enumerate(fields):
            r,c=divmod(i,4)
            tk.Label(form,text=label,bg=BG,fg='white').grid(row=r*2,column=c,sticky='w',padx=6)
            if key=='trainer':
                widget=ttk.Combobox(form,textvariable=self.vars[key],state='readonly',width=22)
                self.trainer_widget=widget
            elif key=='day':
                widget=ttk.Combobox(form,textvariable=self.vars[key],values=DAYS,state='readonly',width=22)
            else:
                widget=tk.Entry(form,textvariable=self.vars[key],width=25)
            widget.grid(row=r*2+1,column=c,padx=6,pady=5,sticky='w')
        bar=tk.Frame(self.window,bg=BG);bar.pack(fill='x',padx=12)
        for title,action in [('Add Class',self.add),('Update Class',self.update),('Delete Class',self.delete),('Clear',self.clear),('View Classes',self.load_classes),('Generate Report',self.report),('Bookings Chart',self.chart)]:
            tk.Button(bar,text=title,command=action,bg='#2980b9',fg='white',padx=9).pack(side='left',padx=3,pady=4)
        search=tk.LabelFrame(self.window,text=' Search and Filter ',bg=BG,fg='white',padx=8,pady=8);search.pack(fill='x',padx=12,pady=8)
        ttk.Combobox(search,textvariable=self.vars['search_by'],values=['Class Name','Class Type','Trainer','Day'],state='readonly',width=16).pack(side='left',padx=3)
        tk.Entry(search,textvariable=self.vars['search'],width=22).pack(side='left',padx=3)
        for label,key in [('Min Fee','min_fee'),('Max Fee','max_fee')]:
            tk.Label(search,text=label,bg=BG,fg='white').pack(side='left',padx=3)
            tk.Entry(search,textvariable=self.vars[key],width=8).pack(side='left',padx=3)
        tk.Button(search,text='Search',command=self.load_classes).pack(side='left',padx=4)
        tk.Button(search,text='Reset',command=self.reset_search).pack(side='left',padx=4)
        frame=tk.Frame(self.window);frame.pack(fill='both',expand=True,padx=12,pady=10)
        cols=['ID','Class Name','Class Type','Trainer','Day','Start Time','Capacity','Fee']
        self.table=ttk.Treeview(frame,columns=cols,show='headings',selectmode='browse')
        for col in cols:
            self.table.heading(col,text=col)
            self.table.column(col,width=130 if col not in ['ID','Capacity','Fee'] else 85)
        self.table.pack(side='left',fill='both',expand=True)
        scrollbar=ttk.Scrollbar(frame,command=self.table.yview);scrollbar.pack(side='right',fill='y')
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.bind('<<TreeviewSelect>>',self.select)

    def load_trainers(self):
        try:
            rows=query('SELECT TrainerID,TrainerName FROM Trainer ORDER BY TrainerName',fetch=True)
            self.trainers={f'{name} (ID {tid})':tid for tid,name in rows}
            self.trainer_widget['values']=list(self.trainers)
        except mysql.connector.Error as exc:
            messagebox.showerror('Database Error',str(exc))

    # Check form inputs before saving anything to MySQL.
    def validate(self):
        name=self.vars['name'].get().strip(); kind=self.vars['type'].get().strip()
        if not name or not kind or len(name)>100 or len(kind)>50:
            raise ValueError('Class name and type are required (maximum 100 and 50 characters).')
        trainer=self.trainers.get(self.vars['trainer'].get())
        if trainer is None: raise ValueError('Choose an existing trainer. Ask Member 1 to add trainers if the list is empty.')
        day=self.vars['day'].get()
        if day not in DAYS: raise ValueError('Select a valid day.')
        try:
            time=datetime.strptime(self.vars['time'].get().strip(),'%H:%M').strftime('%H:%M:%S')
        except ValueError as exc:
            raise ValueError('Start time must be HH:MM (24-hour clock).') from exc
        try:
            capacity=int(self.vars['capacity'].get())
            fee=Decimal(self.vars['fee'].get())
        except (ValueError, InvalidOperation) as exc:
            raise ValueError('Capacity must be a whole number and fee must be numeric.') from exc
        if capacity<=0 or fee<0 or not fee.is_finite() or fee.as_tuple().exponent < -2:
            raise ValueError('Capacity must be positive and fee must be a nonnegative amount with at most 2 decimals.')
        return (name,kind,trainer,day,time,capacity,str(fee))

    # Display classes, including the search and fee filters.
    def load_classes(self):
        sql='''SELECT c.ClassID,c.ClassName,c.ClassType,t.TrainerName,c.DayOfWeek,
          TIME_FORMAT(c.StartTime,'%H:%i'),c.Capacity,c.Fee
          FROM Class c JOIN Trainer t ON c.TrainerID=t.TrainerID WHERE 1=1'''
        params=[]
        term=self.vars['search'].get().strip()
        if term:
            col={'Class Name':'c.ClassName','Class Type':'c.ClassType','Trainer':'t.TrainerName','Day':'c.DayOfWeek'}[self.vars['search_by'].get()]
            sql+=f' AND {col} LIKE %s';params.append('%'+term+'%')
        try:
            for key,operator in [('min_fee','>='),('max_fee','<=')]:
                if self.vars[key].get().strip():
                    value=Decimal(self.vars[key].get())
                    if not value.is_finite() or value<0: raise ValueError('Fee filters must be nonnegative numbers.')
                    sql+=f' AND c.Fee {operator} %s';params.append(str(value))
            rows=query(sql+' ORDER BY c.ClassID',tuple(params),True)
            self.table.delete(*self.table.get_children())
            for row in rows:self.table.insert('', 'end',values=[str(v) for v in row])
        except (ValueError,InvalidOperation,mysql.connector.Error) as exc:
            messagebox.showerror('Search Error',str(exc))

    def select(self,event=None):
        selection=self.table.selection()
        if not selection:return
        values=self.table.item(selection[0],'values');self.selected_id=int(values[0])
        for key,val in zip(['name','type','day','time','capacity','fee'],[values[1],values[2],values[4],values[5],values[6],values[7]]):
            self.vars[key].set(val)
        match=next((k for k in self.trainers if k.startswith(values[3]+' (ID ')), '')
        self.vars['trainer'].set(match)

    def clear(self):
        self.selected_id=None
        for key in ['name','type','trainer','time','capacity','fee']:self.vars[key].set('')
        self.vars['day'].set(DAYS[0])
        for item in self.table.selection():self.table.selection_remove(item)

    def reset_search(self):
        for key in ['search','min_fee','max_fee']:self.vars[key].set('')
        self.load_classes()

    def add(self):
        try:
            data=self.validate()
            query('''INSERT INTO Class (ClassName,ClassType,TrainerID,DayOfWeek,StartTime,Capacity,Fee)
                VALUES (%s,%s,%s,%s,%s,%s,%s)''',data)
            self.clear();self.load_classes();messagebox.showinfo('Success','Class added.')
        except (ValueError,InvalidOperation,mysql.connector.Error) as exc:messagebox.showerror('Cannot Add',str(exc))

    def update(self):
        if self.selected_id is None:return messagebox.showwarning('Select Class','Select a class first.')
        try:
            data=self.validate()
            booked=query("""SELECT COALESCE(MAX(n),0) FROM (SELECT COUNT(*) AS n FROM Booking
                WHERE ClassID=%s AND BookingStatus='Booked' GROUP BY ClassDate) AS counts""",(self.selected_id,),True)[0][0]
            if data[5]<booked:raise ValueError(f'Capacity cannot be less than {booked} existing bookings on a date.')
            query('''UPDATE Class SET ClassName=%s,ClassType=%s,TrainerID=%s,DayOfWeek=%s,
                StartTime=%s,Capacity=%s,Fee=%s WHERE ClassID=%s''',data+(self.selected_id,))
            self.clear();self.load_classes();messagebox.showinfo('Success','Class updated.')
        except (ValueError,InvalidOperation,mysql.connector.Error) as exc:messagebox.showerror('Cannot Update',str(exc))

    def delete(self):
        if self.selected_id is None:return messagebox.showwarning('Select Class','Select a class first.')
        try:
            count=query('SELECT COUNT(*) FROM Booking WHERE ClassID=%s',(self.selected_id,),True)[0][0]
            if count: return messagebox.showerror('Cannot Delete',f'This class has {count} booking record(s).')
            if messagebox.askyesno('Confirm Delete','Delete this class permanently?'):
                query('DELETE FROM Class WHERE ClassID=%s',(self.selected_id,))
                self.clear();self.load_classes()
        except mysql.connector.Error as exc:messagebox.showerror('Database Error',str(exc))

    # Save fully booked class dates as an Excel file.
    def report(self):
        from openpyxl import Workbook
        from openpyxl.styles import Font
        try:
            rows=query('''SELECT c.ClassID,c.ClassName,b.ClassDate,c.Capacity,COUNT(*)
              FROM Booking b JOIN Class c ON c.ClassID=b.ClassID
              WHERE b.BookingStatus='Booked' GROUP BY c.ClassID,c.ClassName,b.ClassDate,c.Capacity
              HAVING COUNT(*)>=c.Capacity ORDER BY b.ClassDate,c.ClassName''',fetch=True)
            path=filedialog.asksaveasfilename(defaultextension='.xlsx',filetypes=[('Excel workbook','*.xlsx')],initialfile='fully_booked_classes.xlsx')
            if not path:return
            wb=Workbook();ws=wb.active;ws.title='Fully Booked'
            ws.append(['Class ID','Class Name','Class Date','Capacity','Booked Places'])
            for row in rows:ws.append(list(row))
            for cell in ws[1]:cell.font=Font(bold=True)
            for col,width in {'A':12,'B':26,'C':18,'D':14,'E':20}.items():ws.column_dimensions[col].width=width
            wb.save(path);messagebox.showinfo('Report Saved',f'Saved {len(rows)} fully booked class date(s).')
        except (mysql.connector.Error,OSError,ValueError) as exc:messagebox.showerror('Report Error',str(exc))

    # Show how many active bookings each class type has.
    def chart(self):
        import matplotlib.pyplot as plt
        try:
            rows=query('''SELECT c.ClassType,COUNT(b.BookingID) FROM Class c
              JOIN Booking b ON b.ClassID=c.ClassID WHERE b.BookingStatus='Booked'
              GROUP BY c.ClassType ORDER BY c.ClassType''',fetch=True)
            if not rows:return messagebox.showinfo('No Data','No active bookings to chart.')
            fig,ax=plt.subplots();ax.bar([r[0] for r in rows],[r[1] for r in rows]);ax.set_title('Bookings by Class Type')
            ax.set_xlabel('Class Type');ax.set_ylabel('Active Bookings');fig.tight_layout();plt.show()
        except mysql.connector.Error as exc:messagebox.showerror('Chart Error',str(exc))

def show_class_management(parent=None):
    if parent is None:
        root=tk.Tk();ClassManagement(root);root.mainloop()
    else:
        ClassManagement(tk.Toplevel(parent))

if __name__=='__main__':show_class_management()


# Auto-generated code from a VirtualWindow
import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x500')
        self.title('Exported Virtual Window')

        self.resizable(False,False)
        self.virtual_window = ctk.CTkFrame(self, fg_color='white', bg_color='lightgrey', width=400, height=500)
        self.virtual_window.pack(expand=True, fill='both')
        self.generic_widget_creator()

    def generic_widget_creator(self):
        ctk.CTkLabel(self.virtual_window, text='Configuraciónes', textvariable='', fg_color='transparent', corner_radius=0, text_color='black', width=0, height=28, font=('Arial', 20), anchor='center', compound='center', justify='center').place(x=6, y=14)
        self.languaje = ctk.CTkComboBox(self.virtual_window, values=[], command=None, state='normal', fg_color=['#F9F9FA', '#343638'], button_color=['#979DA2', '#565B5E'], button_hover_color=['#6E7174', '#7A848D'], dropdown_fg_color=['gray90', 'gray20'], dropdown_hover_color=['gray75', 'gray28'], width=140, height=28, font=('Arial', 12))
        self.languaje.place(x=91, y=50)
        ctk.CTkLabel(self.virtual_window, text='Idioma:', textvariable='', fg_color='transparent', corner_radius=0, text_color='black', width=0, height=28, font=('Arial', 16), anchor='center', compound='center', justify='center').place(x=6, y=50)
        ctk.CTkLabel(self.virtual_window, text='Configuracion de exportacion', textvariable='', fg_color='transparent', corner_radius=0, text_color='black', width=0, height=28, font=('Arial', 20), anchor='center', compound='center', justify='center').place(x=6, y=121)
        ctk.CTkCheckBox(self.virtual_window, text='CTkCheckBox', textvariable=None, onvalue=1, offvalue=0, fg_color=['#3a7ebf', '#1f538d'], text_color='black', width=100, height=24, hover_color=['#325882', '#14375e'], border_width=3, border_color=['#3E454A', '#949A9F'], checkmark_color=['#DCE4EE', 'gray90']).place(x=6, y=243)
        ctk.CTkCheckBox(self.virtual_window, text='CTkCheckBox', textvariable=None, onvalue=1, offvalue=0, fg_color=['#3a7ebf', '#1f538d'], text_color='black', width=100, height=24, hover_color=['#325882', '#14375e'], border_width=3, border_color=['#3E454A', '#949A9F'], checkmark_color=['#DCE4EE', 'gray90']).place(x=6, y=204)
        ctk.CTkCheckBox(self.virtual_window, text='Orientado a objetos', textvariable=None, onvalue=1, offvalue=0, fg_color=['#3a7ebf', '#1f538d'], text_color='black', width=100, height=24, hover_color=['#325882', '#14375e'], border_width=3, border_color=['#3E454A', '#949A9F'], checkmark_color=['#DCE4EE', 'gray90']).place(x=6, y=165)

if __name__ == '__main__':
    app = App()
    app.mainloop()
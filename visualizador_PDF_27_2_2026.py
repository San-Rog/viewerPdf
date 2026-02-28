import streamlit as st
import io
import os
import pymupdf
from streamlit_pdf_viewer import pdf_viewer
from PIL import Image
from streamlit_js_eval import streamlit_js_eval

class messages():
    def __init__(self, status=None):    
        pass    
    
    @st.dialog('⚠️ Falha no app❗')
    def mensError(self, str):
        st.markdown(f'{str} Entre em contato com o administrador da ferramenta!')
    
class saveFiles():
    def __init__(self, down):
        self.down = down
        
    @st.cache_data
    def imgToPdf(_self, *args):
        down = args[0]
        name = args[1]
        ext = args[2]
        down = args[3]
        imgBytes = down.read()
        image = Image.open(io.BytesIO(imgBytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        nameImg = f'new_{name}{ext}'
        image.save(nameImg, quality=100)
        image = Image.open(nameImg)
        fileOut = f'{name}.pdf'
        image.save(fileOut)
        doc = pymupdf.open(fileOut)
        nPages = len(doc)
        doc.close()
        return(fileOut, nPages)
    
    @st.cache_data    
    def pdfToBytes(_self, down):
        bytesData = down.getvalue()
        fileProv = 'prov.pdf'
        with open(fileProv, 'wb') as f:
            f.write(bytesData)
        doc = pymupdf.open(fileProv)
        nPages = len(doc)
        doc.close()
        return(bytesData, nPages)      
        
class main():
    def __init__(self):
        self.setPage()
        self.initiaSession()
        self.widgetsStructure()
        
    def setPage(self):
        st.set_page_config(
        page_title='Leitor simples de PDF',
        page_icon='🕮',
        layout='wide')   
        with open('configCssNew.css') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
                
    def initiaSession(self):
        st.set_page_config(layout="wide")    
        self.size = streamlit_js_eval(js_expressions='window.innerWidth', key='WIDTH')
        self.keys = ['vert', 'horiz', 'control', 'slider', 'inpt', 'butt']
        self.fullSession()       
        self.extImg = ['png', 'ico', 'jpg', 'gif', 'bmp', 'tif']
        self.extPdf = ['pdf']
        self.labels = ['📚 Seleção ou arrastamento de arquivos', 
                       'Vertical', 'Horizontal', 
                       'páginaI', 'paginaS']
        self.extImgPlus = sorted(self.extImg + self.extPdf)
        self.exts = sorted(self.extImg)
        self.nKeys = len(self.keys)
        self.pgsFile = 1
        self.reader = True
        self.controlMap = {
            0: ':material/last_page:',
            1: ':material/chevron_forward:',
            2: ':material/chevron_backward:',
            3: ':material/first_page:',
            4: ':material/rotate_left:', 
            5: ':material/rotate_right:'
        }
        
    def fullSession(self):
        self.keys = ['vert', 'horiz', 'control', 'slider', 'inpt']
        for self.key in self.keys[:2]:
            if self.key not in st.session_state:
                st.session_state[self.key] = False
        for self.key in self.keys[3:5]:
            if self.key not in st.session_state:
                st.session_state[self.key] = 0
            
    def widgetsStructure(self):
        with st.container(border=4):
            colDown, colButts = st.columns([17, 13], vertical_alignment='center')
            self.down = colDown.file_uploader(label=self.labels[0], 
                                              accept_multiple_files=False, 
                                              type=self.extImgPlus, 
                                              max_upload_size=1024*20, 
                                              width='stretch', 
                                              label_visibility='hidden')
            st.space('xxsmall')
            self.checkDisab(0)  
            with colButts:
                colVert, colHoriz, colInpt = st.columns([4.1, 4.1, 3.7], vertical_alignment='center')
                with colVert:
                    st.space(size="small")
                    self.vert = colVert.checkbox(label=self.labels[1], key=self.keys[0], 
                                                 width='stretch', disabled=self.disabs[0], 
                                                 on_change=self.changeCheck, args=('a'), 
                                                 help='Todas as páginas do arquivo são exibidas na tela com paginação vertical.')
                with colHoriz:
                    st.space(size="small")
                    self.horiz = colHoriz.checkbox(label=self.labels[2], key=self.keys[1], 
                                                   width='stretch', disabled=self.disabs[1], 
                                                   on_change=self.changeCheck, args=('b'), 
                                                   help='É exibida na tela uma página por vez.')
                self.inpt = colInpt.number_input(self.labels[3], min_value=0, max_value=self.pgsFile, key=self.keys[4], 
                                                 width='stretch', on_change=self.changeInput, 
                                                 disabled=self.disabs[4], label_visibility='hidden')
                self.sld = st.slider(self.labels[4], min_value=0, max_value=self.pgsFile, key=self.keys[3], 
                                     width='stretch', on_change=self.changeSlider, 
                                     disabled=self.disabs[3], label_visibility='hidden')
        self.checkDisab(1) 
        st.space('xxsmall')
                                                 
    def checkDisab(self, mode):
        if mode == 0:
            if self.down:
                try:
                    self.extractElems()
                    self.disabs = [False for w in range(2)]
                    self.disabs += [True for w in range(2, self.nKeys)]
                except Exception as error:
                    exprError = (f'Na tentativa de ler o arquivo, aconteceu o seguinte erro: \n'
                                 f':blue[**{error}**].')
                    objMens = messages()
                    objMens.mensError(exprError)
                    self.reader = False
                    self.disabs = [True for w in range(self.nKeys)]
            else:
                st.session_state[self.keys [0]] = False
                st.session_state[self.keys [1]] = False
                st.session_state[self.keys [3]] = 0
                st.session_state[self.keys [4]] = 0
                self.disabs = [True for w in range(self.nKeys)]
            if self.reader:
                if self.pgsFile == 1:
                    self.disabs[0] = True
                else:
                    self.disabs[0] = False
                if any([st.session_state[self.keys[0]], st.session_state[self.keys[1]]]):
                    self.disabs[3] = False
                    self.disabs[4] = False
        elif mode == 1:
            valSld = st.session_state[self.keys [3]]
            valInp = st.session_state[self.keys[4]]
            if any([valSld > 0, valInp > 0]):
                statusVert = st.session_state[self.keys[0]]
                statusHoriz = st.session_state[self.keys[1]]
                self.page = valSld
                self.pageRender = []
                self.pageRender = [w+1 for w in range(self.pgsFile)]
                if len(self.fileOutImg.strip()) == 0:
                    self.fileOut = self.fileOutPdf
                else:
                    self.fileOut = self.fileOutImg
                if statusVert:
                    self.showImg()
                if statusHoriz: 
                    if self.fileOut == self.fileOutPdf:
                        self.fileOut = self.fileOutPdf
                        self.pageRender = [valSld]
                    self.showImg()
    
    def showImg(self):    
        st.space('xxsmall')
        with st.container(border=4):
            pdf_viewer(self.fileOut,
                       width=int(self.size*0.95),
                       height=1000,
                       zoom_level=1.0,                    
                       viewer_align='center',             
                       show_page_separator=True, 
                       pages_to_render=self.pageRender,
                       render_text=True,
                       pages_vertical_spacing=10, 
                       annotation_outline_size=3, 
                       scroll_to_page=self.page)
        
    def changeCheck(self, numOne):
        if numOne == 'a':
            if st.session_state[self.keys[0]]:
                st.session_state[self.keys[1]] = False
        if numOne == 'b':
            if st.session_state[self.keys[1]]:
                st.session_state[self.keys[0]] = False
        if any([not st.session_state[self.keys[0]], not st.session_state[self.keys[1]]]):
            st.session_state[self.keys[3]] = 0
            st.session_state[self.keys[4]] = 0         
    
    def changeSlider(self):
        valSlider = st.session_state[self.keys[3]]
        st.session_state[self.keys[4]] = valSlider
    
    def changeInput(self):
        valInput = st.session_state[self.keys[4]]
        st.session_state[self.keys[3]] = valInput
    
    def extractElems(self):
        with st.spinner(f'Aguarde enquanto há o processamento do arquivo {self.down.name}...', 
                        show_time=True):
            name, ext = os.path.splitext(self.down.name)
            extStr = ext.replace('.', '').strip().lower()
            objSave = saveFiles(self.down)
            if extStr in self.extImg: 
                self.fileOutImg, nPags = objSave.imgToPdf(self.down, name, ext, self.down)
            else:
                self.fileOutImg = ''
            if extStr in self.extPdf:
                self.fileOutPdf, nPags = objSave.pdfToBytes(self.down)
            else:
                self.fileOutPdf = ''
            self.pgsFile = nPags
        
if __name__ == '__main__':  
    main()

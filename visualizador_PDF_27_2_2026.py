import streamlit as st
import io
import os
import pymupdf
from streamlit_pdf_viewer import pdf_viewer
from PIL import Image
from streamlit_js_eval import streamlit_js_eval

class saveFiles():
    def __init__(self, down):
        self.down = down
        
    @st.cache_data
    def imgToPdf(_self, *args):
        st.session_state.multFiles = []
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
        st.session_state.sizeImg = nPages
        doc.close()
        st.session_state.multFiles.append(fileOut)
        return fileOut
    
    @st.cache_data    
    def pdfToBytes(_self, down):
        st.session_state.multBytes = []
        bytesData = down.getvalue()
        fileProv = 'prov.pdf'
        with open(fileProv, 'wb') as f:
            f.write(bytesData)
        doc = pymupdf.open(fileProv)
        nPages = len(doc)
        st.session_state.sizeImg = nPages
        doc.close()
        st.session_state.multBytes.append(bytesData)        
        return bytesData
        
    @st.cache_data
    def pdfToPdf(_self, *args):
        st.session_state.multFiles = []
        down = args[0]
        name = args[1]
        allPdfBytes = []
        bytesData = down.getvalue()
        fileProv = f'{name}.pdf'
        with open(fileProv, 'wb') as f:
            f.write(bytesData)
        doc = pymupdf.open(fileProv)
        nPages = len(doc)
        st.session_state.sizeImg = nPages
        for n in range(nPages):
            fileOut = f'{name}_page_{n+1}.pdf'
            st.session_state.multFiles.append(fileOut)
            doc.select([n])
            doc.save(fileOut)
            doc.close()
            with open(fileOut, 'rb') as filePdf:
                pdfBytes = filePdf.read()
            allPdfBytes.append(pdfBytes)
            doc = pymupdf.open(fileProv)
        return allPdfBytes
        
class main():
    def __init__(self):
        self.initiaSession()
        self.widgetsStructure()
                
    def initiaSession(self):
        st.set_page_config(layout="wide")    
        self.size = streamlit_js_eval(js_expressions='window.innerWidth', key='WIDTH')
        self.keys = ['vert', 'horiz', 'control', 'slider', 'inpt', 'butt']
        self.fullSession()       
        self.extImg = ['png', 'ico', 'jpg']
        self.extPdf = ['pdf']
        self.extImgPlus = self.extImg + self.extPdf
        self.exts = sorted(self.extImg)
        self.nKeys = len(self.keys)
        self.controlMap = {
            0: ':material/last_page:',
            1: ':material/chevron_forward:',
            2: ':material/chevron_backward:',
            3: ':material/first_page:',
        }
        
        
    def fullSession(self):
        self.keys = ['vert', 'horiz', 'control', 'slider', 'inpt']
        for self.key in self.keys[:2]:
            if self.key not in st.session_state:
                st.session_state[self.key] = False
        for self.key in self.keys[3:5]:
            if self.key not in st.session_state:
                st.session_state[self.key] = 0
        if 'sizeImg' not in st.session_state:
            st.session_state.sizeImg = 0
        for key in ['multFiles', 'multBytes']:
            if key not in st.session_state:
                st.session_state[key] = []
        
    def widgetsStructure(self):
        with st.container(border=4):
            colDown, colButts = st.columns([18, 14], vertical_alignment='center')
            self.down = colDown.file_uploader(label='📚 Seleção ou arrastamento de arquivos', 
                                              accept_multiple_files=False, 
                                              type=self.extImgPlus, 
                                              max_upload_size=1024*20, 
                                              width='stretch', 
                                              label_visibility='hidden')
            self.checkDisab(0)            
            with colButts:
                colVert, colHoriz, colInpt = st.columns([2.5, 2.5, 3], vertical_alignment='center')
                with colVert:
                    st.space(size="small")
                    self.vert = colVert.checkbox('Vertical', key=self.keys[0], 
                                                 width='stretch', disabled=self.disabs[0], 
                                                 on_change=self.changeCheck, args=('a'))
                with colHoriz:
                    st.space(size="small")
                    self.horiz = colHoriz.checkbox('Horizontal', key=self.keys[1], 
                                                   width='stretch', disabled=self.disabs[1], 
                                                   on_change=self.changeCheck, args=('b'))
                if st.session_state.sizeImg == 0:
                    maxVal = None
                else:
                    maxVal = st.session_state.sizeImg
                self.inpt = colInpt.number_input('página', min_value=0, max_value=maxVal, key=self.keys[4], 
                                                 width='stretch', on_change=self.changeInput, 
                                                 disabled=self.disabs[4], label_visibility='hidden')
                self.sld = st.slider('Página', min_value=0, max_value=maxVal, key=self.keys[3], 
                                          width='stretch', on_change=self.changeSlider, 
                                          disabled=self.disabs[3], label_visibility='hidden')                
        self.checkDisab(1) 
        st.space('xxsmall')
                                                 
    def checkDisab(self, mode):
        if mode == 0:
            if self.down:
                self.extractElems()
                self.disabs = [False for w in range(2)]
                self.disabs += [True for w in range(2, self.nKeys)]
            else:
                for key in ['multFiles', 'multBytes']:
                    st.session_state[key] = []
                st.session_state[self.keys [0]] = False
                st.session_state[self.keys [1]] = False
                st.session_state[self.keys [3]] = 0
                st.session_state[self.keys [4]] = 0
                self.disabs = [True for w in range(self.nKeys)]
            if any([st.session_state[self.keys[0]], st.session_state[self.keys[1]]]):
                self.disabs[3] = False
                self.disabs[4] = False                
        elif mode == 1:
            valSld = st.session_state[self.keys [3]]
            valInp = st.session_state[self.keys[4]]
            if any([valSld > 0, valInp > 0]):
                statusVert = st.session_state[self.keys[0]]
                statusHoriz = st.session_state[self.keys[1]]
                if statusVert:
                    try:
                        self.page = valSld
                        self.fileOut = self.fileOutBytes
                        self.showImg()
                    except:
                        pass
    
    def showImg(self):    
        #st.space('small')
        with st.container(border=None, vertical_alignment='bottom'):
            self.control = st.segmented_control('Fluxo de páginas', 
                                                 options=self.controlMap.keys(), 
                                                 format_func=lambda option: self.controlMap[option],
                                                 width='stretch', key=self.keys[2], 
                                                 disabled=False, label_visibility='hidden')
        st.space('xxsmall')
        #int(self.size*0.95)
        st.write(int(self.size*0.95))
        with st.container(border=4):
            pg = pdf_viewer(self.fileOut,
                       width=900, 
                       height=1000,
                       zoom_level=1.0,                    
                       viewer_align='center',             
                       show_page_separator=True, 
                       render_text=True,
                       pages_vertical_spacing=10, 
                       annotation_outline_size=3, 
                       scroll_to_page=self.page)
            st.write(pg)
        
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
                self.fileOut = objSave.imgToPdf(self.down, name, ext, self.down)
            if extStr in self.extPdf:
                self.fileOutBytes = objSave.pdfToBytes(self.down)
                self.fileOutFiles = objSave.pdfToPdf(self.down, name)[0]
        
if __name__ == '__main__':

    main()


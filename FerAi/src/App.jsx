import {Routes, Route,BrowserRouter} from 'react-router-dom'
import EmotionDetection from './EmotionDetection';

function App() {

  return (
    <>
    <div>
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<EmotionDetection/>} />
        </Routes>
      </BrowserRouter>
    </div>
    </>
  )
}

export default App
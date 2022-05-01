var new_div;

function makePhoto(para1, para2){
    const imgElement = document.createElement('img')
    imgElement.src = para1
    imgElement.style.width='150px'
    imgElement.style.height='150px'
    imgElement.style.objectFit = "cover";
    let word_div = document.createElement('div')
    word_div.appendChild(document.createTextNode(para2))
    let hr = document.createElement("HR");
    new_div = document.createElement('div')
    new_div.className = 'block'
    new_div.appendChild(hr)
    new_div.appendChild(word_div)
    new_div.appendChild(imgElement)
}

function makeError(para1){
    let word_div = document.createElement('div')
    word_div.appendChild(document.createTextNode(para1))
    let hr = document.createElement("HR");
    new_div = document.createElement('div')
    new_div.className = 'block'
    new_div.appendChild(hr)
    new_div.appendChild(word_div)

}

document.getElementsByTagName("form")[0].reset()
document.getElementById("send").addEventListener("click",function(e){
    e.preventDefault()


    let message = document.getElementById("message").value
    let picture = document.getElementById("picture").files[0]

    if(message !== '' && picture !== undefined){

        let formdata = new FormData()
        formdata.append('message', message)
        formdata.append('picture', picture)

        fetch('/send',{
            method : 'POST',
            body: formdata
        }).catch(error => console.error('Error:', error))
        .then(response => response.json()) // 輸出成 json
        .then(function(dict){
            console.log('POST /send 回傳值',dict)
            document.getElementsByTagName("form")[0].reset()

            if ('ok' in dict){

                if (document.querySelector('.block') === null){ //沒有任何留言時
                    makePhoto(dict['img_url'], dict['msg'])
                    document.getElementById('content').appendChild(new_div)                    
                }
                else{ //沒有留言紀錄時
                    makePhoto(dict['img_url'], dict['msg'])
                    document.getElementById('content').insertBefore(new_div,document.querySelector('.block'))
                }
            } 

            else if ('error' in dict){
                if (document.querySelector('.block') === null){
                    makeError(dict['message'])
                    document.getElementById('content').appendChild(new_div)                    
                }
                else{
                    makeError(dict['message'])
                    document.getElementById('content').insertBefore(new_div,document.querySelector('.block'))

                }

            }
            else{
                console.log('不明原因')
            }
        })
    }

    else{
        alert('請輸入圖文資訊')
    }  
});


window.onload=()=>{

    fetch('/send',{
        method : 'GET',
    }).catch(error => console.error('Error:', error))
    .then(response => response.json()) // 輸出成 json
    .then(function(dict){
        console.log('GET /send 回傳值',dict)
        let allfiles = dict['allfiles']
        for (let a=0; a < allfiles.length; a++){
            let msg = allfiles[a][1], img_url = allfiles[a][2]
            makePhoto(img_url, msg)
            document.getElementById('content').appendChild(new_div) 
        }

        document.getElementById('load').style.display='none'
        }
    )



}


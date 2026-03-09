console.log("perfil.js cargado")

document.getElementById("btnCambiarNombre")
.addEventListener("click", () => {

    document.getElementById("cambiarNombreBox")
    .classList.toggle("hidden")

})


document.getElementById("guardarUsername")
.addEventListener("click", async () => {

    const nuevo = document.getElementById("nuevoUsername").value

    // 🔹 VALIDACIÓN
    if(!nuevo.trim()){
        alert("Introduce un nombre válido")
        return
    }

    const res = await fetch("/perfil/api/cambiar-username", {
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify({username:nuevo})
    })

    const data = await res.json()

    if(data.success){
        location.reload()
    }else{
        alert(data.error)
    }

})

document.querySelectorAll(".avatar-option").forEach(img => {

    img.addEventListener("click", async ()=>{

        let avatar = img.src

        // si es avatar local
        if(!avatar.includes("dicebear")){
            avatar = avatar.split("/").pop()
        }

        await fetch("/perfil/api/cambiar-avatar",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body: JSON.stringify({avatar})
        })

        location.reload()

    })

})
async function submit(event){event.preventDefault();const form=event.currentTarget;const button=form.querySelector('button[type=submit]');const note=document.getElementById("login-message");button.disabled=true;note.textContent="Signing in…";note.className="form-message";try{const response=await fetch("/auth/login",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:form.elements.username.value,password:form.elements.password.value})});const data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(data.detail||"Sign-in failed. Check the local synthetic account.");const target=new URLSearchParams(location.search).get("next");const allowed={"/app/user":true,"/app/staff":true,"/app/admin":true};location.assign(Object.hasOwn(allowed,target)?target:"/app/"+data.role);}catch(error){note.textContent=error.message;note.className="form-message error";}finally{button.disabled=false;}}
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login-form");
  form.querySelector("button").innerHTML = relayIcon("next") + " Sign in";
  form.addEventListener("submit", submit);
});

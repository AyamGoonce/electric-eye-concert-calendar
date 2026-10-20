(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.814c7ac0936d51a3.js","sha256":"814c7ac0936d51a39b45fd74a7ebc80f94fec50e3ebf465b08c43a1b57e471af","count":2073,"publishedAt":"2026-10-20T12:30:29Z","state":"calendar-state.json","stateSha256":"bd75d68147a8db81b8005e9bcc81dbd738eb5063a69b9481733dcb75298caba0","sourceState":"calendar-source-state.json","sourceStateSha256":"7bab6caca6f9480424088213e70eaaeaa33e1dea9bfe899f5609edaa4580a216"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());

(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.fe2e1de686178bf3.js","sha256":"fe2e1de686178bf36463c7e1d09f35dcec576d7328a57d01de45232e2f04afe2","count":2473,"publishedAt":"2026-09-15T09:41:17Z","state":"calendar-state.json","stateSha256":"f92f8bcb9a4fd4d7097ee143a42338e8dd76cd5381323de33f3fae792fdfbba4"});
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

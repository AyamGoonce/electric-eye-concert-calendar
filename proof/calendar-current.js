(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.97139c6f390d65b2.js","sha256":"97139c6f390d65b25e40d3cc91d8e29db613d32791003f6813a4ab83588bebb2","count":2194,"publishedAt":"2026-09-19T04:46:42Z","state":"calendar-state.json","stateSha256":"1a0c3871ad16ba1bb0678e085000c537a3c624ab2afde32efb3cc7300c42b1fe"});
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

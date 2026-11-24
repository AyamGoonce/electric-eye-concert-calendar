(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2f9d14429082cbf2.js","sha256":"2f9d14429082cbf23673461193d332590d0b2efd66fcc8c5f70af7c6f4b4e2d7","count":2106,"publishedAt":"2026-11-24T13:17:43Z","state":"calendar-state.json","stateSha256":"18641b61aa9463d9d378fdac4a8770f68a9fd8eb8b00ea5ba961387baa2818e5","sourceState":"calendar-source-state.json","sourceStateSha256":"79e7034e559d9f85c7ec9437ae0353dec93d1cf3f58ee2767363f2ac22b19544"});
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

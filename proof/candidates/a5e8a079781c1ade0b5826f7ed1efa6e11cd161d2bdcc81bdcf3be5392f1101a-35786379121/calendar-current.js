(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a5e8a079781c1ade.js","sha256":"a5e8a079781c1ade0b5826f7ed1efa6e11cd161d2bdcc81bdcf3be5392f1101a","count":2138,"publishedAt":"2026-09-22T21:24:09Z","state":"calendar-state.json","stateSha256":"fa559c814a82d3a989afd8d4ba8c2fb92e8da38323bc06cbcabdbc87d9830eee","sourceState":"calendar-source-state.json","sourceStateSha256":"1a8d297cfe6712a721feabd6fc64e2b91c3e0816d0a28fb10726b841ae8de7a6"});
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

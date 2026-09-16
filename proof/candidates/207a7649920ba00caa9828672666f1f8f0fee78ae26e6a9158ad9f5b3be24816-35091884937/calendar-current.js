(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.207a7649920ba00c.js","sha256":"207a7649920ba00caa9828672666f1f8f0fee78ae26e6a9158ad9f5b3be24816","count":2493,"publishedAt":"2026-09-16T11:48:18Z","state":"calendar-state.json","stateSha256":"0761cb771e3aa99e77042e7bbd1f1fd4900c158df9057b8b24a5b231a90b8ca2"});
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

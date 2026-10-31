(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.0d1ffdd86beb8ea7.js","sha256":"0d1ffdd86beb8ea748dfcfe7ab0031be68c2fd5e3557797f20586ed71d98b9ca","count":2054,"publishedAt":"2026-10-31T05:55:03Z","state":"calendar-state.json","stateSha256":"94e36d0b02b6b02a3408232423adb296645479320608234bc9e2d56f7e6f463c","sourceState":"calendar-source-state.json","sourceStateSha256":"13b33e3884e750330aa0ce1f4ada41b8044bce72ee83342a62554b533e5b65ff"});
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

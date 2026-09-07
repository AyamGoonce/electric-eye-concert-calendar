(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.081d4f8a4c6109c6.js","sha256":"081d4f8a4c6109c6c3fdcacbd6e75e6fa88f3131c70c4e335a819b640c39de45","count":2478,"publishedAt":"2026-09-07T17:11:09Z","state":"calendar-state.json","stateSha256":"2acc3f45015179761c84d11730092c957420d199d74e9be0ed375998dacdfe65"});
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

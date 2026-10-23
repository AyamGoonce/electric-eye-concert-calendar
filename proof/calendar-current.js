(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1ee4ab01099dd699.js","sha256":"1ee4ab01099dd699a2f1fe0f451df7fc54db7609287b4725a20bf189fd853900","count":2084,"publishedAt":"2026-10-23T10:31:02Z","state":"calendar-state.json","stateSha256":"386d8e5f55180385780f8c38f41052428b0292288e8c4fef9e8d401c69a748fe","sourceState":"calendar-source-state.json","sourceStateSha256":"a454347683b6b2a3627704e1a171ba12d59b074bb90dc82240ee10a2b279a10f"});
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

(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.eb4a88d0e6a9881b.js","sha256":"eb4a88d0e6a9881bb92663bcf380787f3a14679d2d42507f4e70f6f33b69e8ef","count":2152,"publishedAt":"2026-10-12T00:38:12Z","state":"calendar-state.json","stateSha256":"6a6e4e16ab8bdcfc3fbdedee6c033eb7fed25c758dc399cea92b01882e46df61","sourceState":"calendar-source-state.json","sourceStateSha256":"bdddd07b1981b1b6b761bfcabd752dcd31349b0c2eb36eee22c2a9bb94a0575c"});
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

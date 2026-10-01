(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.714ebc47b5f4dcb3.js","sha256":"714ebc47b5f4dcb3e1cc3e5c43940dd92b02795468b7d89afa84d69ba2ba35f0","count":2220,"publishedAt":"2026-10-01T06:09:03Z","state":"calendar-state.json","stateSha256":"231c2ccb3ae80d6304e3497c82bf1ecee6c020cdf1f466504e6c8630f204f21d","sourceState":"calendar-source-state.json","sourceStateSha256":"6e66afd64b512989ea123b2a85aa00775580c34de4e9de7ebfe096565740882d"});
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

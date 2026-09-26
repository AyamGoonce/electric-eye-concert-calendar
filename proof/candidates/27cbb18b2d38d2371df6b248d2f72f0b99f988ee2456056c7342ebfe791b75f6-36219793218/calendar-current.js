(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.27cbb18b2d38d237.js","sha256":"27cbb18b2d38d2371df6b248d2f72f0b99f988ee2456056c7342ebfe791b75f6","count":2088,"publishedAt":"2026-09-26T05:11:11Z","state":"calendar-state.json","stateSha256":"94401fa728b1d631f388201df8a13fead10d544ca77a99b8e16ca98a291a6212","sourceState":"calendar-source-state.json","sourceStateSha256":"73a8d74ae9ff0d59723484da54878e4dc6f647d1fa3c24141b0eaa3f1791e321"});
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

(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.277e7cf118292287.js","sha256":"277e7cf11829228707f7338b0b628c84ec7e76bb4fb93e76eaf494ce0b1ed294","count":2136,"publishedAt":"2026-11-14T10:36:28Z","state":"calendar-state.json","stateSha256":"093d036e716f4912c918f6f90795d16e263677db6740122fb0f5cb9cdd778a50","sourceState":"calendar-source-state.json","sourceStateSha256":"8413b82603cd7f5bcca086b60a0e256db295472390f12f8b543d9915e38763e8"});
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
